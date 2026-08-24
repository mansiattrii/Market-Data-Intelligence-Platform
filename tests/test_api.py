# Runs against the real local dev database (already seeded with 99
# companies) rather than an isolated test DB -- see README "What I'd change
# with more time" for that trade-off.
import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="module")
def client():
    # Plain TestClient(app) never fires FastAPI's lifespan, so the
    # connection pool would stay unopened -- must enter as a context
    # manager for startup/shutdown to actually run.
    with TestClient(app) as c:
        yield c


def test_list_companies(client):
    response = client.get("/companies")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) > 0


def test_search_companies_by_name(client):
    response = client.get("/companies", params={"q": "apple"})
    assert response.status_code == 200
    tickers = [c["ticker"] for c in response.json()]
    assert "AAPL" in tickers


def test_get_company_found(client):
    response = client.get("/companies/AAPL")
    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"


def test_get_company_not_found(client):
    response = client.get("/companies/NOTATICKER")
    assert response.status_code == 404


def test_metric_time_series(client):
    response = client.get("/companies/AAPL/metrics/revenue")
    assert response.status_code == 200
    body = response.json()
    assert body["metric"] == "revenue"
    assert len(body["points"]) > 0


def test_metric_time_series_unknown_metric(client):
    response = client.get("/companies/AAPL/metrics/not_a_real_metric")
    assert response.status_code == 404


def test_metric_time_series_unknown_ticker(client):
    response = client.get("/companies/NOTATICKER/metrics/revenue")
    assert response.status_code == 404


def test_metric_time_series_bad_date_range(client):
    response = client.get(
        "/companies/AAPL/metrics/revenue",
        params={"start": "2023-01-01", "end": "2020-01-01"},
    )
    assert response.status_code == 400


def test_top_metric(client):
    series = client.get("/companies/AAPL/metrics/revenue").json()
    period_end = series["points"][-1]["period_end"]

    response = client.get("/metrics/revenue/top", params={"period_end": period_end})
    assert response.status_code == 200
    assert len(response.json()["results"]) > 0


def test_top_metric_unknown_metric(client):
    response = client.get("/metrics/not_a_real_metric/top", params={"period_end": "2023-12-31"})
    assert response.status_code == 404
