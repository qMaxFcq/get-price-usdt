import datetime
import pytz

def get_day_or_night() -> str:
    current_time = datetime.datetime.now(pytz.timezone('Asia/Bangkok')).time()
    if datetime.time(8, 0, 0) <= current_time <= datetime.time(23, 59, 59):
        return "day"
    else:
        return "night"
