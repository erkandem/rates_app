"""
https://docs.sqlalchemy.org/en/13/orm/tutorial.html
http://zetcode.com/db/sqlalchemy/orm/

https://docs.python.org/3.7/library/logging.html
https://docs.python.org/3.7/howto/logging-cookbook.html#logging-cookbook
https://docs.python.org/3.7/howto/logging.html#logging-advanced-tutorial
https://docs.python.org/3.7/howto/logging.html#logging-basic-tutorial

https://en.wikipedia.org/wiki/List_of_HTTP_header_fields

https://sdw-wsrest.ecb.europa.eu/help/
https://stackoverflow.com/questions/16491564/how-to-make-sqlalchemy-in-tornado-to-be-async#16503103
http://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html

http://python-notes.curiousefficiency.org/en/latest/pep_ideas/async_programming.html
https://aiopg.readthedocs.io/en/stable/index.html
https://github.com/fantix/gino

https://sdw.ecb.europa.eu/browseSelection.do?df=true&ec=&dc=&oc=&pb=&rc=&DATASET=3&removeItem=&removedItemList=&mergeFilter=&activeTab=YC&showHide=&MAX_DOWNLOAD_SERIES=500&SERIES_MAX_NUM=50&node=9691417&legendRef=reference&legendNor=

"""

#%%
import json
from datetime import timedelta
from datetime import date
from datetime import datetime as dt
import urllib3
import certifi
from sqlalchemy.orm import sessionmaker
from app.backend.models import EuroYieldCurve
from sqlalchemy.exc import IntegrityError
from app.db.engines import engine

#%%
eu_yield_sets = [
    'YC/B.U2.EUR.4F.G_N_A.SV_C_YM.PY_3M',
    'YC/B.U2.EUR.4F.G_N_A.SV_C_YM.PY_4M',
    'YC/B.U2.EUR.4F.G_N_A.SV_C_YM.PY_6M',
    'YC/B.U2.EUR.4F.G_N_A.SV_C_YM.PY_9M',
    'YC/B.U2.EUR.4F.G_N_A.SV_C_YM.PY_1Y',
    'YC/B.U2.EUR.4F.G_N_A.SV_C_YM.PY_2Y',
    'YC/B.U2.EUR.4F.G_N_A.SV_C_YM.PY_5Y',
    'YC/B.U2.EUR.4F.G_N_A.SV_C_YM.PY_7Y',
    'YC/B.U2.EUR.4F.G_N_A.SV_C_YM.PY_10Y',
    'YC/B.U2.EUR.4F.G_N_A.SV_C_YM.PY_15Y',
    'YC/B.U2.EUR.4F.G_N_A.SV_C_YM.PY_30Y',
]
eu_exp_map = {
    'PY_ON': 1 / 365,
    'PY_1M': 1 / 12,
    'PY_2M': 2 / 12,
    'PY_3M': 3 / 12,
    'PY_4M': 4 / 12,
    'PY_6M': 6 / 12,
    'PY_9M': 9 / 12,
    'PY_1Y': 1,
    'PY_2Y': 2,
    'PY_5Y': 5,
    'PY_7Y': 7,
    'PY_10Y': 10,
    'PY_15Y': 15,
    'PY_30Y': 30,
}
keys = [
    'py_3m',
    'py_4m',
    'py_6m',
    'py_9m',
    'py_1y',
    'py_2y',
    'py_5y',
    'py_7y',
    'py_10y',
    'py_15y',
    'py_30y'
]

https = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED',
    ca_certs=certifi.where(),
)
content_header = {'Accept': 'application/vnd.sdmx.data+json;version=1.0.0-wd'}


def rfr_eu(start_date: date, end_date: date):
    """
    queries the risk free rate for the EUR
    the supplied days will be offset by some dates
    to ensure the essential minimum number of days
    for operations like interpolation.

    In the first half the function retrieves CSV data sets
    and creates a n x m matrix of risk free rates index by date.

    data source: ECB data ware house
    >>> rfr_eu(date(2019, 1, 1), date(2019, 1, 30))

    """
    base = 'https://sdw-wsrest.ecb.europa.eu/service/data/'
    if start_date > end_date:
        raise ValueError('The start_date is supposed to be earlier than end_date')
    params = {
        'startPeriod': start_date.strftime('%Y-%m-%d'),
        'endPeriod': end_date.strftime('%Y-%m-%d'),
    }
    query = [f'{q}={params[q]}' for q in params]
    query_str = '?' + '&'.join(query)
    results = dict()
    for k, dataset in enumerate(eu_yield_sets):
        final_url = base + dataset + query_str
        new_column_name = dataset.split('.')[-1]
        new_column_name = new_column_name.lower()
        r = https.request(
            method='GET',
            url=final_url,
            headers=content_header)
        if r.status == 200:
            data = r.data.decode('utf-8')
            data = json.loads(data)
            observations = data['dataSets'][0]['series']['0:0:0:0:0:0:0']['observations']
            observation_dates = data['structure']['dimensions']['observation'][0]['values']
            results[new_column_name] = {
                dt.strptime(x['id'], '%Y-%m-%d').date(): y[0]
                for x, y in zip(observation_dates, observations.values())}
    return results


#%%


def ecb_update(start_date: date = None, end_date: date = None):
    """ data acquisition """
    if start_date is None:
        start_date = date.today() - timedelta(days=5)
    if end_date is None:
        end_date = date.today()
    new_records = rfr_eu(start_date, end_date)
    dates = new_records[keys[0]]
    records = {d: {k: new_records[k][d] for k in keys} for d in dates}
    for d in records:
        records[d]['dt'] = d
    record_objects = [EuroYieldCurve(records[d]) for d in records]
    Session = sessionmaker(bind=engine)
    session = Session()
    for obj in record_objects:
        try:
            session.add(obj)
            session.commit()
            print(f'{{"dt": "{dt.now()}:, "msg": "added {obj.dt} to db"}},')
        except IntegrityError:
            print(f'A collision for dt: {obj.dt} was caught')
            session.rollback()
    return


def ecb_initial():
    """ initial data acquisition and table creation"""
    from app.backend.models import Base
    Base.metadata.create_all(engine)
    start_date = date(2004, 1, 1)
    years = date.today().year - start_date.year + 1 + 1
    end_dates = [date(start_date.year + y, 1, 1) - timedelta(days=1) for y in range(1, years, 1)]
    start_dates = [date(start_date.year + y -1, 1, 1) for y in range(1, years, 1)]
    start_dates[0] = start_date
    for t0, t1 in zip(start_dates, end_dates):
        ecb_update(t0, t1)
    return


