# --------- Logger ---------
LOG_MAIN = "log_main"
LOG_UPDATE_PRICE = "log_update_price"
LOG_BINANCE = "log_binance"
LOG_BITKUB = "log_bitkub"
LOG_GOOGLE = "log_googlefi"
LOG_INVX = "log_invx"
LOG_OKX = "log_okx"
LOG_Z = "log_z"
LOG_PLUS = "log_plus"
LOG_XS = "log_xs"
# --------- Shop Name ---------
OURS_SHOP = [
    "MoneySwap",
    "MookieGoldenMonkey",
    "Money quick",
    "Never Sleep",
    "เฮงเฮงเฮง",
    "TestTest",
    "WGroup",
    "19TECH",
    "WAZ-Co",
]

# --------- Exchange ---------
EXCHANGE = {"Binance": 1, "Innovestx": 2, "Bitkub": 3, "Bitazza": 4, "Okx": 5, "Z": 6}

# --------- Rate Name ---------
COMPLETE_RATE = 0.950  # 95%

# --------- Coin ---------
ASSETS = ["usdt"]
SYMBOL = "USDT_THB"
TRADE_TYPES = ["buy", "sell"]

# --------- Condition ---------
MIN_AMOUNT_BITKUB = 100000
MIN_AMOUNT_INNOVESTX = 50000
MIN_AMOUNT_XS = 100000


# --------- Limit Price ---------
FILTER_LIMIT_PRICE = {
    "usdt": {
        "day": {
            "1": {
                "row1": {"min": 500000},
                "row2": {"min": 100000},
            },
            "2": {
                "row1": {"min": 300000},
                "row2": {"min": 100000},
            },
            "3": {
                "row1": {"min": 200000},
                "row2": {"min": 100000},
            },
            "4": {
                "row1": {"min": 100000},
                "row2": {"min": 10000},
            },
        },
        "night": {
            "1": {
                "row1": {"min": 500000},
                "row2": {"min": 100000},
            },
            "2": {
                "row1": {"min": 300000},
                "row2": {"min": 100000},
            },
            "3": {
                "row1": {"min": 200000},
                "row2": {"min": 100000},
            },
            "4": {
                "row1": {"min": 100000},
                "row2": {"min": 10000},
            },
        },
    }
}


# --------- Limit Price ---------
FILTER_LIMIT_PRICE_VND = {
    "usdt": {
        "day": {
            "1": {
                "row1": {"min": 200000},
                "row2": {"min": 100000},
            },
        },
        "night": {
            "1": {
                "row1": {"max": 200000, "min": 100000},
                "row2": {"max": 10000, "min": 10000},
            },
        },
    }
}
