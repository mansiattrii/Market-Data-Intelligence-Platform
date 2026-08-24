REQUIRED_FIELDS = ("end", "val", "accn", "fy", "fp", "form", "filed")


def extract_facts(cik, companyfacts, tag_to_metric):
    """Turn one company's raw companyfacts JSON into normalized fact rows.

    Returns (facts, unmapped):
      facts    -- list of dicts ready to insert into the `facts` table
      unmapped -- list of (xbrl_tag, unit) pairs with no entry in xbrl_tag_map
    """
    facts = []
    unmapped = []

    us_gaap = companyfacts.get("facts", {}).get("us-gaap", {})

    for xbrl_tag, tag_data in us_gaap.items():
        units = tag_data.get("units", {})
        metric_key = tag_to_metric.get(xbrl_tag)

        if metric_key is None:
            for unit in units:
                unmapped.append((xbrl_tag, unit))
            continue

        for entry in units.get("USD", []):
            if any(entry.get(field) is None for field in REQUIRED_FIELDS):
                continue

            period_end = entry["end"]
            period_start = entry.get("start", period_end)

            facts.append({
                "cik": cik,
                "metric_key": metric_key,
                "xbrl_tag": xbrl_tag,
                "unit": "USD",
                "period_start": period_start,
                "period_end": period_end,
                "fiscal_year": entry["fy"],
                "fiscal_period": entry["fp"],
                "value": entry["val"],
                "form": entry["form"],
                "filed_date": entry["filed"],
                "accession_number": entry["accn"],
            })

    return facts, unmapped
