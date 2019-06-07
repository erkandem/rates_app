import json
import time
from datetime import datetime as dt
import flask_praetorian
from flask import request
from app.db.redis_db import r


def count_data(data):
    """
    counting function
    t_ = time.time()
    print(f'{(time.time()-t_) * 1000} ms {hash_}')
    """
    if data is None:
        return None
    if len(data) == 0:
        return data
    user = flask_praetorian.current_user().username
    now_ = dt.now()
    hash_ = f'{user}_{now_.year}_{now_.month:02}'
    ts = now_.strftime('%Y-%m-%d-%H:%M:%S.%f')
    meta = {
        'dt': now_.strftime('%Y-%m-%d-%H:%M:%S.%f'),
        'tz': time.timezone,
        'user': user,
        'ip': request.remote_addr,
        'user_agent': str(request.headers.get('User-Agent')),
        'url': request.full_path,
        'n_rows': len(data),
        'n_colums': len(data[0]) - 1
    }
    meta['n_data'] = meta['n_rows'] * meta['n_colums']
    record = json.dumps(meta)
    r.hset(name=hash_, key=ts, value=record)
    return data


def subscriptions_table(version: str):
    """ currently unused """
    return f'''
    CREATE TABLE subscriptions_{version} (
        id integer,
        target_customer varchar, -- personal, enterprise
        billing_period varchar, -- weekly, monthly, quarterly, semiannually, annually
        const_price float, -- 
        var_price float, -- 
        rows_available
        PRIMARY KEY (id)
        );'''


def delete_redis_keys(pattern: str = '*'):
    """ utility after testing deletes EVERYTHING"""
    import redis
    from datetime import datetime as dt
    r = redis.Redis(
        host='localhost',
        port=6379)
    r_keys = r.keys('*')
    print(f'{dt.now()} | Found {len(r_keys)} keys. deleting')
    for key in r_keys:
        r.unlink(key)
    print(f'{dt.now()} | done')
    return
