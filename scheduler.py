from main import main
from schedule import every, run_pending, idle_seconds
import time
import asyncio


def run_main():
    asyncio.run(main())


def tick():
    every(7).seconds.do(run_main)

    while True:
        run_pending()
        time_sleep = idle_seconds()
        time.sleep(max(time_sleep, 1))
        # print(time_sleep)


if __name__ == "__main__":
    tick()
