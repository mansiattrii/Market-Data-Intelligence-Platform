import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

USER_AGENT = os.environ["SEC_USER_AGENT"]

# SEC allows 10 req/sec/IP. We stay well under that on purpose.
REQUEST_DELAY_SECONDS = 0.2

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
TICKERS_CACHE = CACHE_DIR / "company_tickers.json"
COMPANYFACTS_CACHE_DIR = CACHE_DIR / "companyfacts"

_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT})


def _get_with_retry(url, max_attempts=3):
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            time.sleep(REQUEST_DELAY_SECONDS)
            response = _session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < max_attempts:
                time.sleep(1.0 * attempt)
    raise last_exc


def get_ticker_info():
    """Ticker -> {cik, name}, from SEC's full ticker list. Cached to disk.

    We use this file's `title` as the company name, not companyfacts'
    `entityName` -- entityName has been observed to be stale/wrong for at
    least one real CIK (see README "Data problems").
    """
    if TICKERS_CACHE.exists():
        raw = json.loads(TICKERS_CACHE.read_text())
    else:
        raw = _get_with_retry("https://www.sec.gov/files/company_tickers.json")
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        TICKERS_CACHE.write_text(json.dumps(raw))

    return {
        entry["ticker"].upper(): {"cik": entry["cik_str"], "name": entry["title"]}
        for entry in raw.values()
    }


def get_company_facts(cik):
    """Raw companyfacts JSON for one CIK. Cached to disk per-CIK."""
    cache_path = COMPANYFACTS_CACHE_DIR / f"CIK{cik:010d}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
    data = _get_with_retry(url)
    COMPANYFACTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(data))
    return data
