########### Other Packages ###########
import asyncio
import requests
from os import getenv, getcwd
from dotenv import load_dotenv
from sys import path
from pandas import DataFrame, concat

path.append(getcwd())
from database.get_data import get_data_ex, get_symbol_list
from config.config_all import LOG_XS, MIN_AMOUNT_XS, SYMBOL
from helper.logger import Logger


exchange_name = "Xspring"
quantity = 100000
logger = Logger(LOG_XS)


def xspring_key():
    ex_data = get_data_ex()
    ex_xs = ex_data.loc[(ex_data["name"] == exchange_name)]
    xs_api_key = ex_xs["api_key"].iloc[0]
    return xs_api_key


def symbol_list():
    symbol_data = get_symbol_list()
    symbol_res = symbol_data.loc[(symbol_data["name"] == "USDT_THB")]
    split_symbol = symbol_res["name"].str.split("_", expand=True)
    symbol_name = split_symbol[0] + split_symbol[1]
    return symbol_name[0]


async def final_price_xspring():

    try:
        xs_api_key = xspring_key()
        symbol_name = symbol_list()
        url = "https://api-phoenix.xspringdigital.com/api/developer/v1/market/pricing"
        api_key = xs_api_key
        params = {"symbol": symbol_name, "quantity": quantity}
        headers = {"x-api-key": api_key}
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            df = DataFrame(data)
            buy_price = df.loc[
                (df["symbol"] == symbol_name) & (df["quantity"] == quantity), "buy"
            ]["avgUnitPrice"]

            sell_price = df.loc[
                (df["symbol"] == symbol_name) & (df["quantity"] == quantity), "sell"
            ]["avgUnitPrice"]

            results = []

            for price, trade_type in [(sell_price, "buy"), (buy_price, "sell")]:
                update_values = {
                    "exchange_id": int(8),
                    "shop_p2p_name": str("xs"),
                    "trade_type": str(trade_type),
                    "symbol": SYMBOL,
                    "price": round(float(price), 4),
                    "min_amount_order": float(MIN_AMOUNT_XS),
                    "max_amount_order": 0,
                    "complete_rate": 0,
                }

                results.append(DataFrame([update_values]))

            if results:
                final_result = concat(results, ignore_index=True)
                # print(final_result)
                return final_result

        else:
            print("Error:", response.status_code, response.text)

    except Exception as err:
        logger.warn(f"Error from gp_xspring : {err}")
        return DataFrame([])


async def main():
    await final_price_xspring()


# Run the event loop
asyncio.run(main())
