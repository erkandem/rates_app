from sqlalchemy import create_engine


demo_engine = create_engine('sqlite:///:memory:', echo=True)

postgres_db_uri = 'postgres+psycopg2://postgres:postgres@localhost/rates_app'
postgres_db = create_engine(postgres_db_uri)
postgres_pypy = None
