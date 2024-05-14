import requests
import asyncio
import websockets
import json
from pandas import DataFrame, concat
from ast import literal_eval
from os import getcwd
from sys import path

path.append(getcwd())


########### Local Import ###########
from database.get_data import get_data_ex
from config.config_all import LOG_Z, SYMBOL
from helper.logger import Logger
from os import getcwd, getenv
from dotenv import load_dotenv

# try:
#     load_dotenv(".env")
# except ImportError:
#     pass
logger = Logger(LOG_Z)
exchange_name = "Z"

# AUTHORIZATION = getenv("AUTHORIZATION")


async def connect_websocket(url, message=None):
    async with websockets.connect(url) as websocket:
        if message:
            await websocket.send(json.dumps(message))
        response = await websocket.recv()
    return response


def parse_depth_response(response):

    response_data = json.loads(response)

    symbol = response_data["data"]["symbol"]
    buy_price = response_data["data"]["buyPrice"]
    sell_price = response_data["data"]["sellPrice"]

    data = DataFrame(
        {"symbol": [symbol], "buy_price": [buy_price], "sell_price": [sell_price]}
    )

    return data


async def gp_z():
    try:
        url = "wss://ex.z.com/socket"
        subscription_message = {
            "messageType": "SUBSCRIBE_OTC_PRICE",
            "params": {"symbol": SYMBOL},
        }

        # เชื่อมต่อกับ websocket server และส่งคำขอ subscribe
        response = await connect_websocket(url, subscription_message)
        depth = parse_depth_response(response)

        return depth
        # print(response)
    except websockets.exceptions.WebSocketException as err:
        logger.warn(f"Error from gp_innovestx: {err}")
        return DataFrame([])


async def final_price_z():
    try:
        price_from_z = await gp_z()

        if not price_from_z.empty:
            results = []
            for trade_type, column_name in [
                ("buy", "buy_price"),
                ("sell", "sell_price"),
            ]:
                values = {
                    "exchange_id": 6,
                    "shop_p2p_name": "z.com",
                    "trade_type": trade_type,
                    "symbol": SYMBOL,
                    "price": round(float(price_from_z[column_name].iloc[0]), 3),
                    "min_amount_order": 0,
                    "max_amount_order": 0,
                    "complete_rate": 0,
                }
                results.append(DataFrame([values]))

            if results:
                final_result = concat(results, ignore_index=True)
                # print(final_result)
                return final_result
            else:
                print("No valid data found.")
    except Exception as e:
        logger.warn(f"Error from final_price_z: {e}")
        return DataFrame([])


# async def main():
#     await final_price_z()


# # Run the event loop
# asyncio.run(main())
