########### Other Packages ###########
import asyncio
from os import getenv, getcwd
from dotenv import load_dotenv
from pandas import DataFrame, concat, json_normalize
import aiohttp
import sys

sys.path.append(getcwd())

########### Local Import ###########
from config.okx_signature import OkxMerchant
from helper.filter_price import get_filter_price_okx
from helper.logger import Logger
from config.config_all import LOG_OKX, OURS_SHOP, COMPLETE_RATE, SYMBOL
from database.get_data import get_data_ex

# try:
#     load_dotenv(".env")
# except ImportError:
#     pass
logger = Logger(LOG_OKX)
exchange_name = "Okx"

# API_KEY = getenv("API_KEY")
# API_SECRET = getenv("API_SECRET")
# PASSPHRASE = getenv("PASSPHRASE")


def okx_key():
    ex_data = get_data_ex()
    ex_okx = ex_data.loc[(ex_data["name"] == exchange_name)]
    okx_api_key = ex_okx["api_key"].iloc[0]
    okx_api_secret = ex_okx["api_secret"].iloc[0]
    okx_passphrase = ex_okx["passphrase"].iloc[0]
    return okx_api_key, okx_api_secret, okx_passphrase


async def fetch_data():
    okx_api_key, okx_api_secret, okx_passphrase = okx_key()
    merchant = OkxMerchant(okx_api_key, okx_api_secret, okx_passphrase)
    async with aiohttp.ClientSession():
        response = merchant.ad_marketplace_list()
        # print(response)
        return response


async def get_p2p_okx():
    try:
        response = await fetch_data()
        first_response = response["data"]
        all_ads_data = []

        for ad in first_response:
            all_ads_data.extend(ad["buyAds"])
            all_ads_data.extend(ad["sellAds"])

        result = json_normalize(all_ads_data)
        result["creator.nickName"] = result["creator.nickName"].astype(str)
        result["creator.type"] = result["creator.type"].astype(str)
        result["side"] = result["side"].astype(str)
        result["creator.completionRate"] = result["creator.completionRate"].astype(
            float
        )
        result["unitPrice"] = result["unitPrice"].astype(float)
        result["minOrderSize"] = result["minOrderSize"].astype(float)
        result["maxOrderSize"] = result["maxOrderSize"].astype(float)
        result = result[
            [
                "creator.nickName",
                "creator.type",
                "creator.completionRate",
                "unitPrice",
                "minOrderSize",
                "maxOrderSize",
                "side",
            ]
        ]

        # print(result)
        # price_fillter = get_filter_price_okx(result)
        # print(price_fillter)
    except Exception as err:
        logger.warn(f"Error From get_p2p_okx : {err}")
        result = DataFrame([])
    return result


async def final_price_okx():
    try:
        p2p_data_okx = await get_p2p_okx()
        results = []

        if p2p_data_okx.empty:
            logger.warn("P2P OKX Data Not Match Conditions")
            return

        p2p_data_okx = p2p_data_okx.loc[
            (~p2p_data_okx["creator.nickName"].isin(OURS_SHOP))
            & (p2p_data_okx["creator.completionRate"] >= COMPLETE_RATE)
            & (
                (p2p_data_okx["creator.type"] == "certified")
                | (p2p_data_okx["creator.type"] == "diamond")
            )
        ]

        if p2p_data_okx.empty:
            logger.warn("P2P OKX Data Not Match Conditions")
            return

        p2p_data_okx = get_filter_price_okx(p2p_data_okx)

        if not p2p_data_okx:
            logger.warn("P2P OKX Data Not Match Price Range Condition")
            return

        for side in ["buy", "sell"]:
            info = (
                p2p_data_okx[side].iloc[0]
                if side == "buy"
                else p2p_data_okx[side].iloc[-1]
            )
            values = {
                "exchange_id": int(5),
                "shop_p2p_name": str(info["creator.nickName"]),
                "trade_type": str(info["side"]),
                "symbol": SYMBOL,
                "price": round(float(info["unitPrice"]), 3),
                "min_amount_order": float(info["minOrderSize"]),
                "max_amount_order": float(info["maxOrderSize"]),
                "complete_rate": float(info["creator.completionRate"]),
            }
            results.append(DataFrame([values]))

        if results:
            final_result = concat(results, ignore_index=True)
            # print(final_result)
            return final_result
    except Exception as err:
        logger.warn(f"Error From final_price_okx : {err}")


async def main():
    await final_price_okx()


# Run the event loop
asyncio.run(main())
