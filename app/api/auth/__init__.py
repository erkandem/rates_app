from flask_restplus import Resource
from flask_restplus import Namespace
from flask_restplus import fields
from flask_restplus import reqparse
import flask

api = Namespace('Authentication')


login_model = api.model(
    'login', {
        'username': fields.String(description='username', required=True),
        'password': fields.String(description='password', required=True)
    }
)
login_parser = reqparse.RequestParser()
login_parser.add_argument(
    'username',
    type=str,
    required=True,
)
login_parser.add_argument(
    'password',
    type=str,
    required=True,
)

credentials_model = api.model(
    'credentials', {
        'access_token': fields.String(),
    }
)


@api.route('/login', methods=['POST'])
class LoginEndPoint(Resource):
    @api.doc(security=[])
    @api.expect(login_model)
    @api.marshal_with(credentials_model)
    def post(self):
        """Login and get a JWT to consume the data"""
        from app import guard
        req = flask.request.get_json(force=True)
        username = req.get('username', None)
        password = req.get('password', None)
        user = guard.authenticate(username, password)
        token = guard.encode_jwt_token(user)
        return {'access_token': token}

