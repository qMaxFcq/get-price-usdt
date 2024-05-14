from os import getcwd
from sys import path

path.append(getcwd())
from helper.logger import Logger
from config.config_all import LOG_BINANCE
from config.config_all import (
    OURS_SHOP,
    COMPLETE_RATE,
    ASSETS,
    TRADE_TYPES,
    FILTER_LIMIT_PRICE,
    SYMBOL,
)
from helper.filter_price import get_filter_price_binance
from config.times import get_day_or_night
import aiohttp
import asyncio
from pandas import DataFrame, Series, concat, json_normalize
from itertools import product


logger = Logger(LOG_BINANCE)


async def fetch_p2p_binance(
    session, page: int = 1, trade_type: str = None, asset: str = None
):
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        payload = {
            "page": page,
            "rows": 10,  # max and defaut
            "fiat": "THB",
            "tradeType": trade_type,
            "asset": asset,
            "payTypes": ["BANK"],
            "publisherType": "merchant",
        }
        headers = {"Content-Type": "application/json"}
        async with session.post(url, json=payload, headers=headers) as response:
            data = await response.json()
            data["page"] = page
            if data["data"]:
                data["data"][0]["advertiser"]["page"] = page
                # print(data)
                return data
            else:
                pass
    except Exception as e:
        # logger.warn(f"An error occurred in fetch_p2p_binance: {e}")
        return None


async def fetch_all_p2p_binance(trade_type, asset):
    async with aiohttp.ClientSession() as session:
        try:
            first_response = await fetch_p2p_binance(
                session, page=1, trade_type=trade_type, asset=asset
            )
            total_data = first_response.get("total")
            all_page = (total_data // 10) + 2  # +2 bacause range
            tasks = [
                (
                    fetch_p2p_binance(
                        session, page=page, trade_type=trade_type, asset=asset
                    )
                )
                for page in range(2, all_page)
            ]
            responses = await asyncio.gather(*tasks)
            responses.append(first_response)
            return responses
        except Exception as err:
            logger.warn(f"fetch_all_p2p_binance : {err}")


async def get_p2p_binance(trade_type: str, asset: str):
    try:
        responses = await fetch_all_p2p_binance(trade_type, asset)

        if responses is None or not isinstance(responses, list):
            logger.warn("Responses from fetch_all_p2p_binance is not valid.")
            return DataFrame([])

        responses = [resp for resp in responses if resp is not None]

        if not responses:
            logger.warn("No valid responses from fetch_all_p2p_binance.")
            return DataFrame([])

        responses = sorted(responses, key=lambda x: x.get("page", 0))

        response_data = []
        [response_data.extend(data.get("data", [])) for data in responses]

        result = json_normalize(response_data)
        result["advertiser.nickName"] = result["advertiser.nickName"].astype(str)
        result["advertiser.userType"] = result["advertiser.userType"].astype(str)
        result["advertiser.monthFinishRate"] = result[
            "advertiser.monthFinishRate"
        ].astype(float)
        result["adv.price"] = result["adv.price"].astype(float)
        result["adv.minSingleTransAmount"] = result["adv.minSingleTransAmount"].astype(
            float
        )
        result["adv.dynamicMaxSingleTransAmount"] = result[
            "adv.dynamicMaxSingleTransAmount"
        ].astype(float)
        result["advertiser.page"] = result["advertiser.page"].astype(float).ffill()

        result = result[
            [
                "advertiser.nickName",
                "advertiser.userType",
                "advertiser.monthFinishRate",
                "adv.price",
                "adv.minSingleTransAmount",
                "adv.dynamicMaxSingleTransAmount",
                "advertiser.page",
            ]
        ]

    except Exception as err:
        # logger.warn("An unexpected error occurred in get_p2p_binance: ", err)
        result = DataFrame([])
    return result


async def final_price_binance():
    try:
        period = get_day_or_night()
        results = []

        for _, row in DataFrame(
            list(product(ASSETS, TRADE_TYPES)), columns=["asset", "trade_type"]
        ).iterrows():
            p2p_data = await get_p2p_binance(
                trade_type=row.trade_type.upper(), asset=row.asset.upper()
            )

            if p2p_data.empty:
                logger.danger(
                    f"Can't Get Binance P2P Data: {row.asset.lower()}_{row.trade_type.lower()}_{period}"
                )
                continue

            p2p_data = p2p_data.loc[
                (~p2p_data["advertiser.nickName"].isin(OURS_SHOP))
                & (p2p_data["advertiser.monthFinishRate"] >= COMPLETE_RATE)
                & (p2p_data["advertiser.userType"] == "merchant")
            ]

            if p2p_data.empty:
                logger.warn("P2P Data Not Match Conditions")
                continue

            p2p_data_row_1, p2p_data_row_2 = get_filter_price_binance(
                FILTER_LIMIT_PRICE[row.asset][period], p2p_data
            )

            if p2p_data_row_1.empty or p2p_data_row_2.empty:
                logger.warn("P2P Data Not Match Price Range Condition")
                continue

            values = {
                "exchange_id": int(1),
                "shop_p2p_name": str(p2p_data_row_1["advertiser.nickName"].iloc[0]),
                "trade_type": str(row.trade_type.lower()),
                "symbol": SYMBOL,
                "price": round(float(p2p_data_row_1["adv.price"].iloc[0]), 3),
                "min_amount_order": float(
                    p2p_data_row_1["adv.minSingleTransAmount"].iloc[0]
                ),
                "max_amount_order": float(
                    p2p_data_row_1["adv.dynamicMaxSingleTransAmount"].iloc[0]
                ),
                "complete_rate": float(
                    p2p_data_row_1["advertiser.monthFinishRate"].iloc[0]
                ),
            }

            results.append(DataFrame([values]))

        if results:
            final_result = concat(results, ignore_index=True)
            # print(final_result)
            return final_result
    except Exception as err:
        logger.warn("Error from gp_binance : ", err)
        result = DataFrame([])
        return result


async def main():
    await final_price_binance()


# Run the event loop
asyncio.run(main())
