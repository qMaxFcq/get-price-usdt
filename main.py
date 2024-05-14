########### Other Packages ###########
import asyncio
import pandas as pd
from os import getcwd
from sys import path


########### Local Import ###########
from config.config_all import LOG_MAIN
from helper.logger import Logger
from exchange.gp_binance_thb import final_price_binance
from exchange.gp_binance_vnd import final_price_binance_vnd

# from exchange.gp_xs import final_price_xspring
from exchange.gp_okx import final_price_okx
from exchange.gp_z import final_price_z
from exchange.gp_innovestx import final_price_invx
from exchange.gp_bitkub import final_price_bitkub
from exchange.gp_googlefi import final_price_googlefi
from exchange.gp_binance_th import final_binance_th
from database.get_data import get_data_db
from database.update_price import update_data, update_timestamp


path.append(getcwd())
logger = Logger(LOG_MAIN)


async def call_and_append(final_price_function, result_list):
    result_list.append(await final_price_function())


async def main():
    update_timestamp()
    result_list = []
    tasks = [
        call_and_append(final_price_bitkub, result_list),
        call_and_append(final_price_googlefi, result_list),
        call_and_append(final_price_invx, result_list),
        # call_and_append(final_price_z, result_list),
        call_and_append(final_price_okx, result_list),
        # call_and_append(final_price_binance_vnd, result_list),
        call_and_append(final_price_binance, result_list),
        call_and_append(final_binance_th, result_list),
        # call_and_append(final_price_xspring, result_list),
    ]

    await asyncio.gather(*tasks)

    final_result_db = get_data_db()
    final_result = pd.concat(result_list, ignore_index=True)
    final_result = final_result.sort_values(by="exchange_id").reset_index(drop=True)
    combined = pd.concat([final_result_db, final_result], ignore_index=True)
    # print(combined)
    combined["price"] = round(combined["price"], 3)
    df_result = combined.drop_duplicates(
        subset=["exchange_id", "price"], keep=False, ignore_index=True
    )

    # print(df_result)
    final = df_result.drop_duplicates(
        subset=["exchange_id", "trade_type", "symbol"], keep="last", ignore_index=True
    )

    if not final.empty:
        # print(final)
        update_data(final)


if __name__ == "__main__":
    asyncio.run(main())
