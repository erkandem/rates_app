from sqlalchemy import create_engine
import dotenv
import os
dotenv.load_dotenv('.env')
server = os.getenv('RATE_APP_SERVER')
config = os.getenv('RATE_APP_CONFI')

if server == 'REMOTE':
    uri = (
        f"{os.getenv('RATE_APP_DB')}+{os.getenv('RATE_APP_DRIVER')}"
        f"://{os.getenv('RATE_APP_USER')}"
        f":{os.getenv('RATE_APP_PW')}"
        f"@{os.getenv('RATE_APP_HOST')}"
        f":{os.getenv('RATE_APP_PORT')}"
        f"/{os.getenv('RATE_APP_DATABASE_NAME')}"
    )
elif server == 'LOCAL':
    if config == 'PROD':
        uri = (
            f"{os.getenv('RATE_APP_DB_LOC_PROD')}+{os.getenv('RATE_APP_DRIVER_LOC_PROD')}"
            f"://{os.getenv('RATE_APP_USER_LOC_PROD')}"
            f":{os.getenv('RATE_APP_PW_LOC_PROD')}"
            f"@{os.getenv('RATE_APP_HOST_LOC_PROD')}"
            f":{os.getenv('RATE_APP_PORT_LOC_PROD')}"
            f"/{os.getenv('RATE_APP_DATABASE_NAME_LOC_PROD')}"
        )
    elif config == 'DEV':
        uri = 'sqlite:///:memory:'
    else:
        raise ValueError('Value of environment variable RATE_APP_CONFIG not configured')
else:
    raise ValueError('Value of environment variable RATE_APP_SERVER not configured')

postgres_db = create_engine(uri)
