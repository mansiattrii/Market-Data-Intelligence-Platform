def upsert_company(conn, cik, ticker, name):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO companies (cik, ticker, name)
            VALUES (%s, %s, %s)
            ON CONFLICT (cik) DO UPDATE SET ticker = EXCLUDED.ticker, name = EXCLUDED.name
            """,
            (cik, ticker, name),
        )


def upsert_facts(conn, facts):
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO facts (
                cik, metric_key, xbrl_tag, unit, period_start, period_end,
                fiscal_year, fiscal_period, value, form, filed_date, accession_number
            )
            VALUES (
                %(cik)s, %(metric_key)s, %(xbrl_tag)s, %(unit)s, %(period_start)s, %(period_end)s,
                %(fiscal_year)s, %(fiscal_period)s, %(value)s, %(form)s, %(filed_date)s, %(accession_number)s
            )
            ON CONFLICT (cik, metric_key, period_end, period_start) DO UPDATE SET
                value = EXCLUDED.value,
                xbrl_tag = EXCLUDED.xbrl_tag,
                unit = EXCLUDED.unit,
                fiscal_year = EXCLUDED.fiscal_year,
                fiscal_period = EXCLUDED.fiscal_period,
                form = EXCLUDED.form,
                filed_date = EXCLUDED.filed_date,
                accession_number = EXCLUDED.accession_number
            WHERE
                EXCLUDED.filed_date > facts.filed_date
                OR (EXCLUDED.filed_date = facts.filed_date AND EXCLUDED.accession_number > facts.accession_number)
            """,
            facts,
        )


def log_unmapped(conn, cik, unmapped):
    if not unmapped:
        return
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO unmapped_tag_log (cik, xbrl_tag, unit)
            VALUES (%s, %s, %s)
            ON CONFLICT (cik, xbrl_tag) DO NOTHING
            """,
            [(cik, tag, unit) for tag, unit in unmapped],
        )
