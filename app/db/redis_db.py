import redis
import os

server = os.getenv('RATE_APP_SERVER')
config = os.getenv('RATE_APP_CONFI')

if server == 'REMOTE':
    pool = redis.ConnectionPool()
    pool = pool.from_url(url=os.environ.get('REDISCLOUD_URL'))
elif server == 'LOCAL':
    user = os.getenv('RATE_APP_REDIS_LOCAL_USER', '')
    pw = os.getenv('RATE_APP_REDIS_LOCAL_PW', '')
    host = os.getenv('RATE_APP_REDIS_LOCAL_HOST', '127.0.0.1')
    port = os.getenv('RATE_APP_REDIS_LOCAL_PORT', 6379)
    db = os.getenv('RATE_APP_REDIS_LOCAL_DATABASE_NAME', 0)
    db_uri = f'redis://{user}:{pw}@{host}:{port}/{db}'
    pool = redis.ConnectionPool()
    pool = pool.from_url(url=db_uri)
else:
    raise ValueError('Value of environment variable RATE_APP_SERVER not configured')

r = redis.Redis(connection_pool=pool)
