from datetime import datetime

from pydantic import BaseModel


class AnalyticsTotals(BaseModel):
    users: int
    sessions: int
    page_views: int
    prev_users: int
    prev_sessions: int
    prev_page_views: int


class AnalyticsTrendPoint(BaseModel):
    date: str
    users: int
    page_views: int


class AnalyticsTopPage(BaseModel):
    path: str
    views: int
    users: int


class AnalyticsTrafficSource(BaseModel):
    channel: str
    sessions: int


class AnalyticsSummary(BaseModel):
    active_users_now: int
    totals: AnalyticsTotals
    trend: list[AnalyticsTrendPoint]
    top_pages: list[AnalyticsTopPage]
    traffic_sources: list[AnalyticsTrafficSource]
    generated_at: datetime
