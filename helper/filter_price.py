from pandas import DataFrame
from numpy import arange


def get_filter_price_binance(
    filter_limit: dict, p2p_data: DataFrame = None
) -> tuple[DataFrame, DataFrame]:
    for i, row in filter_limit.items():
        filter_row1_min = float(row["row1"]["min"])

        p2p_data_row_1 = p2p_data.loc[
            (
                p2p_data["adv.dynamicMaxSingleTransAmount"]
                - p2p_data["adv.minSingleTransAmount"]
                > 500000
            )
            | (p2p_data["adv.minSingleTransAmount"] > filter_row1_min)
            & (p2p_data["advertiser.page"] == float(i))
        ]

        p2p_data_row_2 = p2p_data.loc[
            (p2p_data["adv.dynamicMaxSingleTransAmount"] > 100000)
            & (p2p_data["advertiser.page"] == float(i))
        ]
        if not p2p_data_row_1.empty and not p2p_data_row_2.empty:
            break
    return p2p_data_row_1, p2p_data_row_2


def get_filter_price_okx(p2p_data: DataFrame = None) -> tuple[DataFrame]:
    ORDER_SIZE_THRESHOLD = 100000
    filtered_data_buy = p2p_data[
        (p2p_data["maxOrderSize"] - p2p_data["minOrderSize"] > ORDER_SIZE_THRESHOLD)
        & (p2p_data["side"] == "buy")
    ]
    filtered_data_sell = p2p_data[
        (p2p_data["maxOrderSize"] - p2p_data["minOrderSize"] > ORDER_SIZE_THRESHOLD)
        & (p2p_data["side"] == "sell")
    ]

    # Print the filtered data for debugging or analysis
    # print(filtered_data_buy)
    # print(filtered_data_sell)
    obj = {"buy": filtered_data_buy, "sell": filtered_data_sell}
    return obj
