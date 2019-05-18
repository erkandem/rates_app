import time
import schedule
from datetime import datetime as dt
from .app import ecb_update, ecb_initial
import asyncio
schedule.every().day.at("22:12").do(ecb_update)


def main():
    while True:
        schedule.run_pending()
        print(f'It is {dt.now()}')
        time.sleep(60)


if __name__ == '__main__':
    main()
