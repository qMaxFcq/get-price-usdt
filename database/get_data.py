from os import getcwd
from sys import path

path.append(getcwd())
from database.connection import connect_db, close_connect_db
from pandas import DataFrame
from decimal import Decimal
from datetime import datetime


def get_data_db() -> DataFrame:
    try:
        connection, cursor = connect_db(), None

        if connection is not None:
            query = "SELECT * FROM price_history WHERE (exchange_id, trade_type, created_at) IN (SELECT exchange_id, trade_type, MAX(created_at) FROM price_history WHERE symbol = 'USDT' GROUP BY exchange_id, trade_type) AND symbol = 'USDT' ORDER BY exchange_id"
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()

            rows = [
                {
                    "exchange_id": int(row[1]),
                    "shop_p2p_name": str(row[2]),
                    "trade_type": str(row[3]),
                    "symbol": str(row[4]),
                    "price": round(float(row[5]), 3),
                    "min_amount_order": float(row[6]),
                    "max_amount_order": float(row[7]),
                    "complete_rate": float(row[8]),
                }
                for row in data
            ]
            df = DataFrame(rows)

            return df
        else:
            print("Error: Unable to establish a database connection.")
            return DataFrame()

    except Exception as e:
        print(f"Error from get_data_db: {e}")
        return DataFrame()
    finally:
        close_connect_db(connection)


def get_data_ex() -> DataFrame:
    try:
        connection, cursor = connect_db(), None

        if connection:
            query = "SELECT id, name, api_key, api_secret, passphrase, authorization FROM config_exchange ORDER BY id"
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()

            columns = [
                "id",
                "name",
                "api_key",
                "api_secret",
                "passphrase",
                "authorization",
            ]
            df_exchange = DataFrame(
                [
                    dict(
                        zip(
                            columns,
                            (
                                int(row[0]),
                                str(row[1]),
                                str(row[2]),
                                str(row[3]),
                                str(row[4]),
                                str(row[5]),
                            ),
                        )
                    )
                    for row in data
                ]
            )

            return df_exchange
        else:
            print("Error: Unable to establish a database connection.")
            return DataFrame()

    except Exception as e:
        print(f"Error from get_data_ex: {e}")
        return DataFrame()
    finally:
        close_connect_db(connection)


def get_symbol_list() -> DataFrame:
    try:
        connection, cursor = connect_db(), None
        if connection:
            query = "SELECT id, name FROM symbol ORDER BY id"
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchall()

            columns = [
                "id",
                "name",
            ]
            df_exchange = DataFrame(
                [
                    dict(
                        zip(
                            columns,
                            (
                                int(row[0]),
                                str(row[1]),
                            ),
                        )
                    )
                    for row in data
                ]
            )

            return df_exchange
        else:
            print("Error: Unable to establish a database connection.")
            return DataFrame()

    except Exception as e:
        print(f"Error from get_symbol_list: {e}")
        return DataFrame()
    finally:
        close_connect_db(connection)


# # Example usage
# result = get_symbol_list()
# print(result)
