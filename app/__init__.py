"""
https://www.fullstackpython.com/flask.html

"""
from flask import Flask
import flask_sqlalchemy
import flask_praetorian
import flask_cors
from .api import api
from .backend import ecb_initial
from app.db.engines import postgres_db_uri
db = flask_sqlalchemy.SQLAlchemy()
guard = flask_praetorian.Praetorian()
cors = flask_cors.CORS()


class User(db.Model):
    """
    A generic user model that
    might be used by an app
    powered by flask-praetorian
    """
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

'''
with app.app_context():
    db.create_all()
    db.session.add(User(
        username='fda',
        password=guard.encrypt_password('abc123'),
        roles='admin,operator,mashine'
    ))
    db.session.commit()
'''
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = postgres_db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
cors.init_app(app)
guard.init_app(app, User)
api.init_app(app)



if __name__ == '__main__':
    app.run(debug=True)
