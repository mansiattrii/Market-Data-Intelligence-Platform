import argparse

from db import get_connection
from ingest.companies import TICKERS
from ingest.fetch import get_ticker_info, get_company_facts
from ingest.load import log_unmapped, upsert_company, upsert_facts
from ingest.normalize import extract_facts


def load_tag_map(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT xbrl_tag, metric_key FROM xbrl_tag_map")
        return dict(cur.fetchall())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    tickers = TICKERS[: args.limit]

    conn = get_connection()
    tag_to_metric = load_tag_map(conn)
    ticker_info = get_ticker_info()

    total_facts = 0
    total_unmapped = 0
    skipped = []

    for ticker in tickers:
        info = ticker_info.get(ticker)
        if info is None:
            print(f"[skip] {ticker}: not found in SEC ticker list")
            skipped.append(ticker)
            continue

        cik, name = info["cik"], info["name"]

        try:
            companyfacts = get_company_facts(cik)
        except Exception as exc:
            print(f"[skip] {ticker}: fetch failed ({exc})")
            skipped.append(ticker)
            continue

        facts, unmapped = extract_facts(cik, companyfacts, tag_to_metric)

        upsert_company(conn, cik, ticker, name)
        if facts:
            upsert_facts(conn, facts)
        log_unmapped(conn, cik, unmapped)
        conn.commit()

        total_facts += len(facts)
        total_unmapped += len(unmapped)
        print(f"[ok] {ticker} ({name}): {len(facts)} facts, {len(unmapped)} unmapped tag observations")

    conn.close()

    print()
    print(f"Companies processed: {len(tickers) - len(skipped)}/{len(tickers)}")
    print(f"Total fact rows upserted: {total_facts}")
    print(f"Total unmapped tag observations logged: {total_unmapped}")
    if skipped:
        print(f"Skipped: {', '.join(skipped)}")


if __name__ == "__main__":
    main()
