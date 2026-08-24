# Curated tickers, deliberately spanning sectors -- different industries
# tend to use different XBRL tags for the same underlying concept, which is
# exactly what stresses the normalization layer. First 20 are the initial
# validation subset (`--limit 20`); the rest extend it to ~100.
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "JPM", "BAC", "WFC", "V", "MA",
    "WMT", "TGT", "JNJ", "PFE", "KO",
    "XOM", "CVX", "GE", "CAT", "BA",

    "NVDA", "TSLA", "GS", "MS", "COST",
    "HD", "LOW", "UNH", "MRK", "ABBV",
    "PEP", "MCD", "SBUX", "HON", "UPS",
    "FDX", "ORCL", "CRM", "ADBE", "INTC",
    "AMD", "QCOM", "CSCO", "IBM", "TXN",
    "NFLX", "DIS", "CMCSA", "T", "VZ",
    "NKE", "TJX", "SPGI", "BLK", "SCHW",
    "AXP", "C", "USB", "PNC", "ADP",
    "PYPL", "INTU", "NOW", "UBER", "ABNB",
    "BKNG", "EBAY", "ETSY", "SHOP", "F",
    "GM", "DE", "MMM", "LMT", "RTX",
    "NOC", "GD", "EMR", "ITW", "PG",
    "CL", "KMB", "GIS", "K", "HSY",
    "MDLZ", "STZ", "MO", "PM", "DUK",
    "SO", "NEE", "AEP", "EXC", "D",
    "XEL", "ED", "WEC", "ES", "LULU",
]
