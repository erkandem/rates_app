import os
import time
import schedule
import urllib3
import certifi
import dotenv
from datetime import datetime as dt
dotenv.load_dotenv('.env')

https = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where(),
)

dev_ = 'http://127.0.0.1:5000'
host_ = 'https://rfr.herokuapp.com'
url = f'{dev_}/{os.getenv("RFR_APP_UPDATE_URI")}'


def job():
    response = https.request(method='PUT', url=url)
    print(f'{dt.now()} | Executed job. Got {response.status}')


schedule.every().monday.at('15:00').do(job)
schedule.every().tuesday.at('15:00').do(job)
schedule.every().wednesday.at('15:00').do(job)
schedule.every().thursday.at('15:00').do(job)
schedule.every().friday.at('15:00').do(job)

if __name__ == '__main__':
    print(f'{dt.now()} | Started schedule')
    while True:
        schedule.run_pending()
        time.sleep(60)
