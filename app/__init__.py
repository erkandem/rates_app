"""
https://www.fullstackpython.com/flask.html

"""
import os
import json
import flask
import flask_sqlalchemy
import flask_praetorian
import flask_cors
from app.api import api
from app.db.engines import db_uri
from app.backend import ecb_update
from sqlalchemy.exc import IntegrityError, InvalidRequestError

db = flask_sqlalchemy.SQLAlchemy()
guard = flask_praetorian.Praetorian()
cors = flask_cors.CORS()


class User(db.Model):
    __bind_key__ = 'application_data'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True)  # username = db.Column(db.VARCHAR(200), unique=True)
    password = db.Column(db.Text)  # password = db.Column(db.VARCHAR(200))
    roles = db.Column(db.Text)  # roles = db.Column(db.VARCHAR(200))
    is_active = db.Column(db.Boolean, default=True, server_default='true')  # is_active = db.Column(db.Boolean, default=True)
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


def assign_plugins(app):
    db.init_app(app)
    cors.init_app(app)
    guard.init_app(app, User)
    api.init_app(app)


def migrate_test_users(app):
    with open('migration/test_users.json', 'r') as f:
        pw_dict = json.load(f)

    with app.app_context():
        db.create_all(bind='application_data')
        for username in list(pw_dict):
            try:
                db.session.add(User(
                    username=username,
                    password=guard.encrypt_password(pw_dict[username]),
                    roles='subscriber'
                ))
                db.session.commit()
            except InvalidRequestError or IntegrityError:
                print(f' user `{username}` already in db')
    return


def create_app():
    app = flask.Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key'
    app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
    app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_BINDS'] = {
        'application_data': os.getenv('RATES_APP_USER_DB_URL')
    }
    assign_plugins(app)
    # migrate_test_users(app) # used for loadtesting
    return app


app = create_app()


'''
try:
    with app.app_context():
        db.create_all(bind='application_data')
        db.session.add(User(
            username='fda',
            password=guard.encrypt_password('abc123'),
            roles='admin,operator,mashine,subscriber'
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
