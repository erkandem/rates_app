"""
https://www.fullstackpython.com/flask.html

"""
import os
import flask
import flask_sqlalchemy
import flask_praetorian
import flask_cors
from app.api import api
from app.db.engines import db_uri
from app.backend import ecb_update
import json
import time
from uuid import uuid4
from flask import request

import sqlalchemy
'''
import redis
r = redis.Redis(
    host='localhost',
    port=6379)
'''
db = flask_sqlalchemy.SQLAlchemy()
guard = flask_praetorian.Praetorian()
cors = flask_cors.CORS()

'''
class LogData(db.Model):
    __bind_key__ = 'application_data'
    id = db.Column(db.Integer, primary_key=True)
    ukey = db.Column(db.Text)
    dt = db.Column(db.Float)
    user = db.Column(db.Text)
    tz = db.Column(db.Integer)
    url = db.Column(db.Text)
    ip = db.Column(db.Text)
    user_agent = db.Column(db.Text)
    n_row = db.Column(db.Integer)
    n_colum = db.Column(db.Integer)
    n_data = db.Column(db.Integer)

    def __repr__(self):
        return f'<LogKey: {self.key}r>'

    def init_from_dict(self, d: dict):
        self.__dict__.update(d)
'''
'''

def send_meta_data_to_db(ukey, meta_data, database: str):
    if database == 'redis':
        val = json.dumps(meta_data)
        r.set(name=ukey, value=val)
    elif database == 'sqlite':
        meta_data['ukey'] = ukey
        entry = LogData()
        entry.init_from_dict(meta_data)
        db.session.add(entry)
        db.session.commit()
    else:
        raise NotImplementedError
'''
def count_data(*args, **kwargs):
    return
'''
def count_data(data: list, database: str = None):
    """counting function
    """
    d = time.time()
    user = flask_praetorian.current_user().username

    meta = {
        'dt':  	time.time(),
        'user': user,
        'tz': time.timezone,
        'url': request.full_path,
        'ip': request.remote_addr,
        'user_agent': str(request.headers.get('User-Agent')),
        'n_row': len(data),
        'n_colum': len(data[0]) - 1
    }
    meta['n_data'] = meta['n_row'] * meta['n_colum']
    ukey  = uuid4().__str__()
    if database is not None:
        send_meta_data_to_db(ukey, meta, database=database)
    #print(f'{(time.time() - d) * 1000} ms')
    return
'''

class User(db.Model):
    __bind_key__ = 'application_data'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    roles = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, server_default='true')

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except Exception:
            return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id

    def is_valid(self):
        return self.is_active


"""
def subscriptions_table(version: str):
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
"""

def assign_plugins(app):
    db.init_app(app)
    cors.init_app(app)
    guard.init_app(app, User)
    api.init_app(app)


def create_app():
    app = flask.Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key'
    app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
    app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_BINDS'] = {
        'application_data': 'sqlite:////home/kan/dev/py/ecb/ecb/application_data.db'
    }
    assign_plugins(app)
    return app


app = create_app()
'''
try:
    with app.app_context():
        db.create_all(bind='application_data')
        db.session.add(User(
            username='fda',
            password=guard.encrypt_password('abc123'),
            roles='admin,operator,mashine'
        ))
        db.session.commit()
except sqlalchemy.exc.IntegrityError:
    print('Database exists already')
'''

@app.route('/')
def landing_page():
    return flask.render_template('index.html')


@app.route('/redoc')
def redoc():
    return flask.render_template('redoc.html')


@app.route('/' + os.getenv('RFR_APP_UPDATE_URI'), methods=['PUT'])
def run_backend_update():
    """update via RPC"""
    ecb_update()
    return 'executed', 200


if __name__ == '__main__':
    app.run(debug=False)
