from datetime import datetime as dt
from flask_restplus import Resource
from flask_restplus import Namespace
from flask_restplus import fields
from flask_restplus import reqparse
from app.db.engines import engine
import flask_praetorian
from app.backend.app import keys as db_columns

api = Namespace('Euro-Area Risk Free Rate')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                           #
#                        Get a single column                                #
#                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

single_ts_model = api.model(
    'single_ts', {
        'dt': fields.Date(),
        'value': fields.Float()
    }
)
single_ts_parser = reqparse.RequestParser()
single_ts_parser.add_argument(
    'startdate',
    type=str,
    required=True,
    help='yyyy-mm-dd'
)
single_ts_parser.add_argument(
    'enddate',
    type=str,
    required=False,
    help='yyyy-mm-dd'
)
single_ts_parser.add_argument(
    'strip',
    type=str,
    required=True,
    choices=db_columns,
    help='',
)


def select_single_time_series(args: dict) -> str:
    startdate = dt.strptime(args['startdate'], '%Y-%m-%d').date()
    if args['enddate'] is None:
        where = f"WHERE dt = '{startdate}' "
    else:
        enddate = dt.strptime(args['enddate'], '%Y-%m-%d').date()
        where = f"WHERE dt BETWEEN '{startdate}' AND '{enddate}' "
    return f'''
        SELECT dt, {args["strip"]} AS value
        FROM euro_area_yield_curve
        {where};'''


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                           #
#                   Get the latest record in the DB                         #
#                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

single_ts_latest_parser = reqparse.RequestParser()
single_ts_latest_parser.add_argument(
    'strip',
    type=str,
    required=True,
    choices=db_columns,
    help='',
)


def select_single_latest(args: dict) -> str:
    return f'''
        SELECT dt, {args["strip"]} AS value
        FROM euro_area_yield_curve
        ORDER BY dt DESC
        LIMIT 1;'''


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                           #
#            Deliver all available maturities of the yield curve            #
#                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

curve_model = api.model(
    'curve_ts', {
        'dt': fields.Date(),
        'py_3m': fields.Float(),
        'py_4m': fields.Float(),
        'py_6m': fields.Float(),
        'py_9m': fields.Float(),
        'py_1y': fields.Float(),
        'py_2y': fields.Float(),
        'py_5y': fields.Float(),
        'py_7y': fields.Float(),
        'py_10y': fields.Float(),
        'py_15y': fields.Float(),
        'py_30y': fields.Float(),
    }
)
curve_parser = reqparse.RequestParser()
curve_parser.add_argument(
    'startdate',
    type=str,
    required=True,
    help='yyyy-mm-dd'
)
curve_parser.add_argument(
    'enddate',
    type=str,
    required=False,
    help='yyyy-mm-dd'
)


def select_curve(args: dict) -> str:
    startdate = dt.strptime(args['startdate'], '%Y-%m-%d').date()
    if args['enddate'] is None:
        where = f"WHERE dt = '{startdate}' "
    else:
        enddate = dt.strptime(args['enddate'], '%Y-%m-%d').date()
        where = f"WHERE dt BETWEEN '{startdate}' AND '{enddate}' "
    return f'''
        SELECT   dt, {' ,'.join(db_columns)}
        FROM euro_area_yield_curve
        {where};'''

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                           #
#                      Get the latest yield curve set                       #
#                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def select_curve_latest() -> str:
    return f'''
        SELECT dt,  {' ,'.join(db_columns)}
        FROM euro_area_yield_curve
        ORDER BY dt DESC
        LIMIT 1;'''


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                           #
#                     Routes                                                #
#                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


@api.route('/curve/single', methods=['GET'])
class SingleTimeSeries(Resource):
    @api.marshal_with(single_ts_model)
    @api.expect(single_ts_parser)
    # @flask_praetorian.auth_required
    def get(self):
        """Access a single maturity"""
        args = single_ts_parser.parse_args()
        sql = select_single_time_series(args)
        with engine.connect() as con:
            curs = con.execute(sql)
            data = curs.fetchall()
        return data


@api.route('/curve/single/latest', methods=['GET'])
class SingleTimeSeriesLatest(Resource):
    @api.marshal_with(single_ts_model)
    @api.expect(single_ts_latest_parser)
    # @flask_praetorian.auth_required
    def get(self):
        """ Access the latest set for a single maturity """
        args = single_ts_latest_parser.parse_args()
        sql = select_single_latest(args)
        with engine.connect() as con:
            curs = con.execute(sql)
            data = curs.fetchall()
        return data


@api.route('/curve', methods=['GET'])
class YieldCurve(Resource):
    @api.marshal_with(curve_model)
    @api.expect(curve_parser)
    # @flask_praetorian.auth_required
    def get(self):
        """Get the full yield curve"""
        args = curve_parser.parse_args()
        sql = select_curve(args)
        with engine.connect() as con:
            curs = con.execute(sql)
            data = curs.fetchall()
        return data


@api.route('/curve/latest', methods=['GET'])
class YieldCurveLatest(Resource):
    @api.marshal_with(curve_model)
    # @flask_praetorian.auth_required
    def get(self):
        """Get the latest yield curve data set in the database"""
        sql = select_curve_latest()
        with engine.connect() as con:
            curs = con.execute(sql)
            data = curs.fetchall()
        return data

