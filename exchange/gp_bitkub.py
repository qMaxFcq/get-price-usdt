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


async def gp_bitkub(symbol: str) -> DataFrame:
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = "https://api.bitkub.com/api/market/depth"
            params = {"sym": symbol, "lmt": 100}
            response = await session.get(url, params=params)
            data: list = await response.json()
            depth: DataFrame = DataFrame(data)
            if depth.empty:
                raise Exception("Can Get Depth Data from bitkub")
            depth = depth.apply(Series.explode, axis=1)
            depth.columns = ("ask_price", "ask_amount", "bid_price", "bid_amount")
            return depth

    except Exception as err:
        # logger.warn(f"Error from gp_bitkub : {err}")
        return None


# def cal avg price
# async def final_price_bitkub():
#     try:
#         p2p_data_bitkub = await gp_bitkub(symbol="THB_USDT")
#         result_list = []
#         if not p2p_data_bitkub.empty:
#             bid_price, ask_price = find_min_amount(
#                 depth=p2p_data_bitkub, maxi=MIN_AMOUNT_BITKUB
#             )

#             for price, trade_type in [(bid_price, "buy"), (ask_price, "sell")]:
#                 update_values = {
#                     "exchange_id": int(3),
#                     "shop_p2p_name": str("bitkub"),
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
#             # print(final_result)
#             return final_result
#     except Exception as err:
#         logger.warn(f"Error from final_price_bitkub : {err}")
#         return DataFrame([])


async def final_price_bitkub():
    try:
        p2p_data_bitkub = await gp_bitkub(symbol="THB_USDT")
        result_list = []
        if not p2p_data_bitkub.empty:
            ask_price = p2p_data_bitkub.iloc[0]["ask_price"]
            bid_price = p2p_data_bitkub.iloc[0]["bid_price"]

            for price, trade_type in [
                (bid_price, "buy"),
                (ask_price, "sell"),
            ]:
                update_values = {
                    "exchange_id": int(3),
                    "shop_p2p_name": str("bitkub"),
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
    await final_price_bitkub()


asyncio.run(main())
