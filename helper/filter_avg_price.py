from pandas import DataFrame


def find_min_amount(depth: DataFrame, maxi: int) -> tuple[float, float]:
    depth["ask_cost"] = (depth["ask_price"] * depth["ask_amount"]).cumsum()
    depth["bid_cost"] = (depth["bid_price"] * depth["bid_amount"]).cumsum()
    len_depth_ask = depth.loc[depth["ask_cost"] <= maxi].shape[0]
    depth_ask = depth.iloc[0 : len_depth_ask + 1, :]
    len_depth_bid = depth.loc[depth["bid_cost"] <= maxi].shape[0]
    depth_bid = depth.iloc[0 : len_depth_bid + 1, :]
    sum_bid_amt = round(depth_bid["bid_amount"].sum(), 8)
    avg_bid_price = round(depth_bid["bid_cost"].iloc[-1] / sum_bid_amt, 4)
    sum_ask_amt = round(depth_ask["ask_amount"].sum(), 8)
    avg_ask_price = round(depth_ask["ask_cost"].iloc[-1] / sum_ask_amt, 4)

    return avg_bid_price, avg_ask_price
