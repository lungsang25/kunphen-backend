"""Thin client for the GA4 Data API.

Deliberately speaks REST over `google-auth`'s AuthorizedSession rather than using
the `google-analytics-data` SDK: the SDK pulls in grpcio, which is heavy enough to
matter for the Vercel function bundle, and we only need two endpoints.
"""

import base64
import binascii
import json
import threading

from fastapi import HTTPException, status
from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from app.config import settings

API_ROOT = "https://analyticsdata.googleapis.com/v1beta"
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
TIMEOUT = 20

_session: AuthorizedSession | None = None
_session_lock = threading.Lock()


class AnalyticsUnavailable(HTTPException):
    """GA4 is unconfigured or upstream failed; surfaced to Studio as a readable error."""

    def __init__(self, detail: str, status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE):
        super().__init__(status_code=status_code, detail=detail)


def _load_credentials() -> service_account.Credentials:
    raw = settings.ga4_credentials_json.strip()
    # Accept either raw JSON or base64-wrapped JSON so the same value survives
    # being pasted into a Vercel env var.
    if not raw.startswith("{"):
        try:
            raw = base64.b64decode(raw, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError, ValueError):
            raise AnalyticsUnavailable(
                "GA4_CREDENTIALS_JSON is neither valid JSON nor valid base64"
            )
    try:
        info = json.loads(raw)
    except json.JSONDecodeError:
        raise AnalyticsUnavailable("GA4_CREDENTIALS_JSON is not valid JSON")

    try:
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    except ValueError as exc:
        raise AnalyticsUnavailable(f"GA4 service account key is invalid: {exc}")


def _get_session() -> AuthorizedSession:
    """One authorized session per process; it refreshes its own access token."""
    global _session
    if _session is None:
        with _session_lock:
            if _session is None:
                _session = AuthorizedSession(_load_credentials())
    return _session


def _post(method: str, body: dict) -> dict:
    if not settings.ga4_configured:
        raise AnalyticsUnavailable(
            "Google Analytics is not configured on the server "
            "(set GA4_PROPERTY_ID and GA4_CREDENTIALS_JSON)"
        )

    url = f"{API_ROOT}/properties/{settings.ga4_property_id}:{method}"
    try:
        res = _get_session().post(url, json=body, timeout=TIMEOUT)
    except Exception as exc:  # network, token refresh, DNS...
        raise AnalyticsUnavailable(f"Could not reach Google Analytics: {exc}")

    if res.status_code == 403:
        raise AnalyticsUnavailable(
            "Google Analytics denied access — grant the service account Viewer "
            "on this property, and confirm GA4_PROPERTY_ID is the numeric id",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )
    if not res.ok:
        detail = res.text[:300]
        try:
            detail = res.json()["error"]["message"]
        except (ValueError, KeyError, TypeError):
            pass
        raise AnalyticsUnavailable(
            f"Google Analytics request failed ({res.status_code}): {detail}",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )
    return res.json()


def run_report(body: dict) -> dict:
    return _post("runReport", body)


def run_realtime_report(body: dict) -> dict:
    return _post("runRealtimeReport", body)


def dimension(row: dict, index: int = 0) -> str:
    values = row.get("dimensionValues") or []
    if index >= len(values):
        return ""
    return values[index].get("value") or ""


def metric(row: dict, index: int = 0) -> int:
    """GA4 returns every metric as a string; totals can come back as floats."""
    values = row.get("metricValues") or []
    if index >= len(values):
        return 0
    try:
        return int(float(values[index].get("value") or 0))
    except (TypeError, ValueError):
        return 0
