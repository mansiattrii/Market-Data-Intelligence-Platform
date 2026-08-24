-- Market Data Intelligence Platform -- schema
-- Applied once, directly (see README "Design decisions" for why no
-- migration tool is used at this scale).

CREATE TABLE companies (
    cik         INTEGER PRIMARY KEY,
    ticker      TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE metrics (
    metric_key    TEXT PRIMARY KEY,
    display_name  TEXT NOT NULL,
    unit          TEXT NOT NULL
);

CREATE TABLE xbrl_tag_map (
    xbrl_tag    TEXT PRIMARY KEY,
    metric_key  TEXT NOT NULL REFERENCES metrics(metric_key)
);

CREATE TABLE facts (
    id                BIGSERIAL PRIMARY KEY,
    cik               INTEGER NOT NULL REFERENCES companies(cik),
    metric_key        TEXT NOT NULL REFERENCES metrics(metric_key),
    xbrl_tag          TEXT NOT NULL REFERENCES xbrl_tag_map(xbrl_tag),
    unit              TEXT NOT NULL,
    period_start      DATE NOT NULL,
    period_end        DATE NOT NULL,
    fiscal_year       INTEGER NOT NULL,
    fiscal_period     TEXT NOT NULL,
    value             NUMERIC NOT NULL,
    form              TEXT NOT NULL,
    filed_date        DATE NOT NULL,
    accession_number  TEXT NOT NULL,
    UNIQUE (cik, metric_key, period_end, period_start)
);

-- Speeds up "top companies by metric for a period" (api/queries.py
-- get_top_for_metric): metric_key + period_end aren't the leading columns
-- of any other index. See NUMBERS.md Phase 4 for before/after timings.
CREATE INDEX idx_facts_metric_period ON facts (metric_key, period_end);

CREATE TABLE unmapped_tag_log (
    id           SERIAL PRIMARY KEY,
    cik          INTEGER NOT NULL REFERENCES companies(cik),
    xbrl_tag     TEXT NOT NULL,
    unit         TEXT,
    observed_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (cik, xbrl_tag)
);

-- Canonical metric catalog (v1: 6 concepts, all USD-denominated).
INSERT INTO metrics (metric_key, display_name, unit) VALUES
    ('revenue',             'Revenue',                    'USD'),
    ('net_income',          'Net Income',                 'USD'),
    ('total_assets',        'Total Assets',                'USD'),
    ('total_liabilities',   'Total Liabilities',           'USD'),
    ('stockholders_equity', 'Stockholders Equity',         'USD'),
    ('operating_cash_flow', 'Operating Cash Flow',         'USD');

-- Normalization layer: raw XBRL tags -> canonical metric.
-- Companies vary in which of these they use for the same concept; this is
-- what fixes the "inconsistent tagging" problem.
INSERT INTO xbrl_tag_map (xbrl_tag, metric_key) VALUES
    ('Revenues', 'revenue'),
    ('RevenueFromContractWithCustomerExcludingAssessedTax', 'revenue'),
    ('RevenueFromContractWithCustomerIncludingAssessedTax', 'revenue'),
    ('SalesRevenueNet', 'revenue'),
    ('SalesRevenueGoodsNet', 'revenue'),

    ('NetIncomeLoss', 'net_income'),
    ('ProfitLoss', 'net_income'),

    ('Assets', 'total_assets'),

    ('Liabilities', 'total_liabilities'),

    ('StockholdersEquity', 'stockholders_equity'),
    ('StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest', 'stockholders_equity'),

    ('NetCashProvidedByUsedInOperatingActivities', 'operating_cash_flow'),
    ('NetCashProvidedByUsedInOperatingActivitiesContinuingOperations', 'operating_cash_flow');
