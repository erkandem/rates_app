from flask_restplus import Api

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in':   'header',
        'name': 'Authorization'
    }
}

api = Api(
        title='Euro Area Rates API',
        version='1.0.0',  # keep 3 digits style for Node.js
        description='Because ECB warehouse takes too long',
        # terms_url='/api/v1/terms-and-conditions',
        prefix='/api/v1',
        doc='/swaggerui',
        authorizations=authorizations,
        security='apikey',
        license='Client: BSD3, Data: See Manual, ',
        # license_url='/api/v1/licence',
        contact='Volsurf - Sales',
        contact_url='https://volsurf.com',
        contact_email='info@volsurf.com')
'''
        # default_id=default_id,
        # default='default',
        # default_label='Default namespace',
        # validate=None,
        # tags=None,
        # ordered=False,
        # default_mediatype='application/json',
        # decorators=None,
        # catch_all_404s=False,
        # serve_challenge_on_401=False,
        # format_checker=None,
'''

from .rates import euro_ns
api.add_namespace(euro_ns, path='/euro')

from flask_praetorian import PraetorianError
PraetorianError.register_error_handler_with_flask_restplus(api)

