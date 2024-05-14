from pandas import DataFrame, Series, concat
import asyncio
import aiohttp
from os import getcwd
from sys import path

path.append(getcwd())
from config.config_all import LOG_BITKUB, MIN_AMOUNT_BITKUB, SYMBOL

from helper.logger import Logger
from helper.filter_avg_price import find_min_amount

logger = Logger(LOG_BITKUB)


async def gp_binance_th(symbol: str) -> DataFrame:
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = "https://api.binance.th/api/v1/depth"
            params = {"symbol": symbol, "limit": 50}
            response = await session.get(url, params=params)
            data: list = await response.json()
            bids = data["bids"]
            asks = data["asks"]

            bids_df = DataFrame(bids, columns=["bid_price", "bid_amount"])
            asks_df = DataFrame(asks, columns=["ask_price", "ask_amount"])

            # convert to numeric type
            bids_df["bid_price"] = bids_df["bid_price"].astype(float)
            bids_df["bid_amount"] = bids_df["bid_amount"].astype(float)
            asks_df["ask_price"] = asks_df["ask_price"].astype(float)
            asks_df["ask_amount"] = asks_df["ask_amount"].astype(float)

            depth = concat([asks_df, bids_df], axis=1)

            return depth

    except Exception as err:
        print(f"Error from gp_binance_th : {err}")
        return None


# def cal avg price
# async def final_binance_th():
#     try:
#         p2p_data_binance_th = await gp_binance_th(symbol="usdtthb")
#         result_list = []
#         if not p2p_data_binance_th.empty:
#             bid_price, ask_price = find_min_amount(
#                 depth=p2p_data_binance_th, maxi=MIN_AMOUNT_BITKUB
#             )

#             for price, trade_type in [(bid_price, "buy"), (ask_price, "sell")]:
#                 update_values = {
#                     "exchange_id": int(8),
#                     "shop_p2p_name": str("binance_th"),
#                     "trade_type": str(trade_type),
#                     "symbol": SYMBOL,
#                     "price": round(float(price), 3),
#                     "min_amount_order": float(MIN_AMOUNT_BITKUB),
#                     "max_amount_order": 0,
#                     "complete_rate": 0,
#                 }

#                 result_list.append(DataFrame([update_values]))

#         if result_list:
#             final_result = concat(result_list, ignore_index=True)
#             return final_result
#     except Exception as err:
#         logger.warn(f"Error from final_binance_th : {err}")
#         return DataFrame([])


async def final_binance_th():
    try:
        p2p_data_binance_th = await gp_binance_th(symbol="usdtthb")
        result_list = []
        if not p2p_data_binance_th.empty:
            ask_price = p2p_data_binance_th.iloc[0]["ask_price"]
            bid_price = p2p_data_binance_th.iloc[0]["bid_price"]

            for price, trade_type in [
                (bid_price, "buy"),
                (ask_price, "sell"),
            ]:
                update_values = {
                    "exchange_id": int(9),
                    "shop_p2p_name": str("binance_th"),
                    "trade_type": str(trade_type),
                    "symbol": SYMBOL,
                    "price": round(float(price), 3),
                    "min_amount_order": float(MIN_AMOUNT_BITKUB),
                    "max_amount_order": 0,
                    "complete_rate": 0,
                }

                result_list.append(DataFrame([update_values]))

        if result_list:
            final_result = concat(result_list, ignore_index=True)
            # print(final_result)
            return final_result
    except Exception as err:
        logger.warn(f"Error from final_binance_th : {err}")
        return DataFrame([])


async def main():
    await final_binance_th()


# Run the event loop
asyncio.run(main())
