import requests
import asyncio
import yfinance as yf
from pandas import DataFrame, concat
from bs4 import BeautifulSoup
from os import getcwd
from sys import path

path.append(getcwd())
from config.config_all import LOG_BITKUB, SYMBOL
from helper.logger import Logger

logger = Logger(LOG_BITKUB)

API_GOOGLEFIN = "https://www.google.com/finance/quote/USD-THB"


async def gp_googlefi():
    try:
        response = requests.get(API_GOOGLEFIN)
        soup = BeautifulSoup(response.text, "html.parser")
        exchange_rate_elem = soup.select_one(".YMlKec.fxKbKc")
        ticker = "USDTHB=X"

        if exchange_rate_elem is not None:
            exchange_rate = exchange_rate_elem.text
            google_rate = round(float(exchange_rate), 2)
        else:
            data = yf.download(ticker)
            usd_to_thb_price = data["Close"].iloc[-1]
            google_rate = round(usd_to_thb_price, 2)
            logger.info("Price from Yahoo Finance")

        return google_rate
    except Exception as err:
        logger.warn(f"Error from gp_googlefi : {err}")


async def final_price_googlefi():
    try:
        results = []
        usdt_google = await gp_googlefi()
        values = {
            "exchange_id": int(4),
            "shop_p2p_name": str("googlefi"),
            "trade_type": str("mid"),
            "symbol": SYMBOL,
            "price": float(usdt_google),
            "min_amount_order": 0,
            "max_amount_order": 0,
            "complete_rate": 0,
        }

        results.append(DataFrame([values]))

        if results:
            final_result = concat(results, ignore_index=True)
            # print(final_result)
            return final_result
    except Exception as err:
        logger.warn(f"Error from final_price_googlefi : {err}")
        return DataFrame([])

    # update_data("Bitazza", values)
    # print(usdt_google)


async def main():
    await final_price_googlefi()


# Run the event loop
asyncio.run(main())
