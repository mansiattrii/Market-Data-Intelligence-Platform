from datetime import date, datetime

from pydantic import BaseModel


class CompanySummary(BaseModel):
    cik: int
    ticker: str
    name: str


class CompanyDetail(BaseModel):
    cik: int
    ticker: str
    name: str
    created_at: datetime


class MetricPoint(BaseModel):
    period_start: date
    period_end: date
    fiscal_year: int
    fiscal_period: str
    value: float
    form: str
    filed_date: date


class MetricTimeSeries(BaseModel):
    ticker: str
    metric: str
    unit: str
    points: list[MetricPoint]


class TopMetricEntry(BaseModel):
    ticker: str
    name: str
    value: float


class TopMetricResponse(BaseModel):
    metric: str
    period_end: date
    results: list[TopMetricEntry]
