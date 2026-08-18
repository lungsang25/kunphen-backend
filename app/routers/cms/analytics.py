import time
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query

from app.schemas.analytics import (
    AnalyticsSummary,
    AnalyticsTopPage,
    AnalyticsTotals,
    AnalyticsTrafficSource,
    AnalyticsTrendPoint,
)
from app.services import ga4
from app.services.auth import get_current_admin

router = APIRouter(
    prefix="/analytics",
    tags=["cms-analytics"],
    dependencies=[Depends(get_current_admin)],
)

# The historical reports are four upstream calls and the numbers only move once a
# day, so serve them from a short in-process cache. Realtime is fetched every
# request so the "active users now" tile stays live on refresh.
CACHE_TTL_SECONDS = 300
_cache: dict[int, tuple[float, dict]] = {}

CURRENT = "current"
PREVIOUS = "previous"


def _date_ranges(days: int) -> list[dict]:
    """Current window plus the equally long window immediately before it."""
    return [
        {"startDate": f"{days - 1}daysAgo", "endDate": "today", "name": CURRENT},
        {"startDate": f"{2 * days - 1}daysAgo", "endDate": f"{days}daysAgo", "name": PREVIOUS},
    ]


def _range_index(report: dict) -> int | None:
    """Position of the synthetic `dateRange` dimension in a multi-range report."""
    headers = report.get("dimensionHeaders") or []
    for i, header in enumerate(headers):
        if header.get("name") == "dateRange":
            return i
    return None


def _fetch_totals(days: int) -> AnalyticsTotals:
    report = ga4.run_report(
        {
            "dateRanges": _date_ranges(days),
            "metrics": [
                {"name": "totalUsers"},
                {"name": "sessions"},
                {"name": "screenPageViews"},
            ],
        }
    )
    rows = report.get("rows") or []
    idx = _range_index(report)

    by_range: dict[str, dict] = {}
    for position, row in enumerate(rows):
        # Fall back to row order if the dateRange dimension is ever absent:
        # ranges come back in the order they were requested.
        key = ga4.dimension(row, idx) if idx is not None else ""
        if key not in (CURRENT, PREVIOUS):
            key = CURRENT if position == 0 else PREVIOUS
        by_range[key] = row

    current = by_range.get(CURRENT, {})
    previous = by_range.get(PREVIOUS, {})
    return AnalyticsTotals(
        users=ga4.metric(current, 0),
        sessions=ga4.metric(current, 1),
        page_views=ga4.metric(current, 2),
        prev_users=ga4.metric(previous, 0),
        prev_sessions=ga4.metric(previous, 1),
        prev_page_views=ga4.metric(previous, 2),
    )


def _fetch_trend(days: int) -> list[AnalyticsTrendPoint]:
    report = ga4.run_report(
        {
            "dateRanges": [{"startDate": f"{days - 1}daysAgo", "endDate": "today"}],
            "dimensions": [{"name": "date"}],
            "metrics": [{"name": "totalUsers"}, {"name": "screenPageViews"}],
            "orderBys": [{"dimension": {"dimensionName": "date"}}],
            "limit": days,
        }
    )

    points: dict[date, tuple[int, int]] = {}
    for row in report.get("rows") or []:
        raw = ga4.dimension(row)  # YYYYMMDD
        try:
            day = datetime.strptime(raw, "%Y%m%d").date()
        except ValueError:
            continue
        points[day] = (ga4.metric(row, 0), ga4.metric(row, 1))

    # GA4 drops days with no traffic, and its "today" follows the property's
    # timezone rather than the server's — so anchor the window on the newest day
    # GA actually reported and back-fill the rest with zeros.
    anchor = max(points) if points else datetime.now(timezone.utc).date()
    trend = []
    for offset in range(days - 1, -1, -1):
        day = anchor - timedelta(days=offset)
        users, page_views = points.get(day, (0, 0))
        trend.append(
            AnalyticsTrendPoint(date=day.isoformat(), users=users, page_views=page_views)
        )
    return trend


def _fetch_top_pages(days: int) -> list[AnalyticsTopPage]:
    report = ga4.run_report(
        {
            "dateRanges": [{"startDate": f"{days - 1}daysAgo", "endDate": "today"}],
            "dimensions": [{"name": "pagePath"}],
            "metrics": [{"name": "screenPageViews"}, {"name": "totalUsers"}],
            "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
            "limit": 10,
        }
    )
    return [
        AnalyticsTopPage(
            path=ga4.dimension(row) or "/",
            views=ga4.metric(row, 0),
            users=ga4.metric(row, 1),
        )
        for row in report.get("rows") or []
    ]


def _fetch_traffic_sources(days: int) -> list[AnalyticsTrafficSource]:
    report = ga4.run_report(
        {
            "dateRanges": [{"startDate": f"{days - 1}daysAgo", "endDate": "today"}],
            "dimensions": [{"name": "sessionDefaultChannelGroup"}],
            "metrics": [{"name": "sessions"}],
            "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
            "limit": 8,
        }
    )
    return [
        AnalyticsTrafficSource(
            channel=ga4.dimension(row) or "Unassigned",
            sessions=ga4.metric(row, 0),
        )
        for row in report.get("rows") or []
    ]


def _fetch_active_users() -> int:
    try:
        report = ga4.run_realtime_report({"metrics": [{"name": "activeUsers"}]})
    except ga4.AnalyticsUnavailable:
        # A realtime hiccup shouldn't blank out the whole dashboard.
        return 0
    rows = report.get("rows") or []
    return ga4.metric(rows[0]) if rows else 0


def _historical(days: int) -> dict:
    cached = _cache.get(days)
    if cached and time.monotonic() - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]

    data = {
        "totals": _fetch_totals(days),
        "trend": _fetch_trend(days),
        "top_pages": _fetch_top_pages(days),
        "traffic_sources": _fetch_traffic_sources(days),
    }
    _cache[days] = (time.monotonic(), data)
    return data


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(days: int = Query(28, ge=1, le=365)):
    return AnalyticsSummary(
        active_users_now=_fetch_active_users(),
        generated_at=datetime.now(timezone.utc),
        **_historical(days),
    )
