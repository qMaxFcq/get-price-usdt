import asyncio
import websockets
import json
from pandas import DataFrame, concat
from ast import literal_eval
from os import getcwd, getenv
from dotenv import load_dotenv
import sys

sys.path.append(getcwd())

########### Local Import ###########
from helper.filter_avg_price import find_min_amount
from config.config_all import LOG_INVX, MIN_AMOUNT_INNOVESTX, SYMBOL
from helper.logger import Logger

logger = Logger(LOG_INVX)


async def connect_websocket(url, message):
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
    return response


def parse_depth_response(response):
    column_data = [
        "Col1",
        "Col2",
        "Col3",
        "Col4",
        "Col5",
        "Col6",
        "price",
        "Col8",
        "amount",
        "side",
    ]
    response_data = literal_eval(json.loads(response).get("o"))
    data = DataFrame(response_data, columns=column_data)

    depth = DataFrame()
    depth["ask_price"] = data.loc[data["side"] == 1, "price"].reset_index(drop=True)
    depth["ask_amount"] = data.loc[data["side"] == 1, "amount"].reset_index(drop=True)
    depth["bid_price"] = data.loc[data["side"] == 0, "price"].reset_index(drop=True)
    depth["bid_amount"] = data.loc[data["side"] == 0, "amount"].reset_index(drop=True)

    dtypes = {
        "ask_price": float,
        "ask_amount": float,
        "bid_price": float,
        "bid_amount": float,
    }
    depth = depth.astype(dtypes).reset_index(drop=True)
    return depth


async def gp_innovestx(symbol: str = None):
    try:
        url = "wss://api-digitalassets.scbs.com/WSGateway"
        subscription_message = {
            "m": 0,
            "i": 18,
            "n": "SubscribeLevel2",
            "o": '{"OMSId":1,"InstrumentId":15,"Depth":50}',
        }

        response = await connect_websocket(url, subscription_message)
        depth = parse_depth_response(response)
        # print(depth)
        return depth
    except websockets.exceptions.WebSocketException as err:
        logger.warn(f"Error from gp_innovestx: {err}")
        return DataFrame([])


async def final_price_invx():
    try:
        results = []
        p2p_data_invx = await gp_innovestx()
        if not p2p_data_invx.empty:
            bid_price, ask_price = find_min_amount(
                depth=p2p_data_invx, maxi=MIN_AMOUNT_INNOVESTX
            )

            for price, trade_type in [(bid_price, "buy"), (ask_price, "sell")]:
                update_values = {
                    "exchange_id": int(2),
                    "shop_p2p_name": str("invx"),
                    "trade_type": str(trade_type),
                    "symbol": SYMBOL,
                    "price": round(float(price), 2),
                    "min_amount_order": float(MIN_AMOUNT_INNOVESTX),
                    "max_amount_order": 0,
                    "complete_rate": 0,
                }

                results.append(DataFrame([update_values]))
        if results:
            final_result = concat(results, ignore_index=True)
            # print(final_result)
            return final_result
    except Exception as err:
        logger.warn(f"Error from get_innovestx_depth: {err}")
        return DataFrame([])


async def main():
    await final_price_invx()


# Run the event loop
asyncio.run(main())
