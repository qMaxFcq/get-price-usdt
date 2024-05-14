from database.connection import connect_db, close_connect_db
from config.config_all import LOG_UPDATE_PRICE
from helper.logger import Logger
from config.config_all import EXCHANGE

logger = Logger(LOG_UPDATE_PRICE)


# def update_data(data: any) -> bool:

#     resp: bool = False
#     try:
#         connection, cursor = connect_db(), None
#         query = "INSERT INTO price_history (exchange_id, shop_p2p_name, trade_type, symbol, price, min_amount_order, max_amount_order, complete_rate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
#         cursor = connection.cursor()

#         data_tuples = [tuple(x) for x in data.values]
#         if data_tuples:
#             cursor.executemany(query, data_tuples)
#             connection.commit()
#             logger.info(f"Data inserted successfully")
#         else:
#             pass

#     except Exception as e:
#         logger.warn(f"Error from update_data: {e}")
#     finally:
#         close_connect_db(connection)


def update_data(data: any) -> bool:
    try:
        connection = connect_db()
        cursor = connection.cursor()

        for _, row in data.iterrows():
            if row["exchange_id"] in [1, 5]:
                query = "INSERT INTO price_history (exchange_id, shop_p2p_name, trade_type, symbol, price, min_amount_order, max_amount_order, complete_rate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                values = (
                    row["exchange_id"],
                    row["shop_p2p_name"],
                    row["trade_type"],
                    row["symbol"],
                    row["price"],
                    row["min_amount_order"],
                    row["max_amount_order"],
                    row["complete_rate"],
                )
                cursor.execute(query, values)
            else:
                query = f"UPDATE price_history SET price = {row['price']}, min_amount_order = {row['min_amount_order']}, max_amount_order = {row['max_amount_order']}, complete_rate = {row['complete_rate']} WHERE exchange_id = {row['exchange_id']} AND trade_type = '{row['trade_type']}' AND symbol = '{row['symbol']}'"
                cursor.execute(query)

        connection.commit()
        logger.info("Data updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error from update_data: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        close_connect_db(connection)


def update_timestamp() -> bool:

    try:
        connection, cursor = connect_db(), None
        query = "UPDATE bot_timestamp SET updated_at = now() WHERE id = 1"
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()

    except Exception as e:
        logger.warn(f"Error from update_timestamp: {e}")
    finally:
        close_connect_db(connection)
