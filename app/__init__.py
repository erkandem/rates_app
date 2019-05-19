"""
https://www.fullstackpython.com/flask.html

"""
import flask
import flask_sqlalchemy
import flask_praetorian
import flask_cors
from .api import api
from app.db.engines import db_uri
from .backend import ecb_update

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

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
cors.init_app(app)
guard.init_app(app, User)
api.init_app(app)


@app.route('/')
def landing_page():
    return flask.render_template('index.html')


@app.route('/redoc')
def redoc():
    return flask.render_template('redoc.html')


@app.route('/HWLNMMM9ZC8RgdW9WKG3pVntoC8uQUWTyYHdEPikpakoRDr34o')
def run_backend_update():
    ecb_update()
    return 'executed', 200

if __name__ == '__main__':
    app.run(debug=True)
