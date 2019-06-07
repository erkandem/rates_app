import os
from datetime import datetime as dt
from flask_restplus import Resource
from flask_restplus import Namespace
from flask_restplus import fields
from flask_restplus import reqparse
from app.db.engines import engine
import flask_praetorian
from app.backend.app import keys as db_columns
from app.metering import count_data

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
    required=False,
    help='yyyy-mm-dd'
)
single_ts_parser.add_argument(
    'enddate',
    type=str,
    required=False,
    help='yyyy-mm-dd'
)
single_ts_parser.add_argument(
    'maturity',
    type=str,
    required=True,
    choices=db_columns,
    help='',
)


def select_maturity_in_one(args: dict) -> str:
    startdate = args['startdate']
    enddate = args['enddate']
    maturity = args["maturity"]
    if startdate is not None and enddate is None:
        return f'''SELECT dt,  {maturity} AS value
                    FROM  euro_area_yield_curve
                    WHERE dt = '{startdate}';'''
    elif startdate is None and enddate is None:
        return f'''SELECT dt,  {maturity} AS value
                    FROM  euro_area_yield_curve
                    ORDER BY dt DESC
                    LIMIT 1;'''
    elif startdate is None and enddate is not None:
        return f'''SELECT dt, {maturity} AS value
                    FROM  euro_area_yield_curve
                    WHERE dt = '{enddate}';'''
    elif startdate is not None and enddate is not None:
        return f'''SELECT dt,  {maturity} AS value
                    FROM  euro_area_yield_curve
                    WHERE dt BETWEEN '{startdate}' AND '{enddate}';'''


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
    required=False,
    help='yyyy-mm-dd'
)
curve_parser.add_argument(
    'enddate',
    type=str,
    required=False,
    help='yyyy-mm-dd'
)


def select_curve_in_one(args: dict) -> str:
    startdate = args['startdate']
    enddate = args['enddate']
    if startdate is not None and enddate is None:
        return f'''SELECT  dt,  {' ,'.join(db_columns)}
                    FROM euro_area_yield_curve
                    WHERE dt = '{startdate}';'''
    elif startdate is None and enddate is None:
        return f'''SELECT  dt,  {' ,'.join(db_columns)}
                    FROM euro_area_yield_curve
                    ORDER BY dt DESC
                    LIMIT 1;'''
    elif startdate is None and enddate is not None:
        return f'''SELECT  dt,  {' ,'.join(db_columns)}
                    FROM euro_area_yield_curve
                    WHERE dt = '{enddate}';'''
    elif startdate is not None and enddate is not None:
        return f'''SELECT  dt,  {' ,'.join(db_columns)}
                    FROM euro_area_yield_curve
                    WHERE dt BETWEEN '{startdate}' AND '{enddate}';'''


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                           #
#                     Service                                               #
#                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def serve_curve(args: dict) -> dict:
    sql = select_curve_in_one(args)
    with engine.connect() as con:
        curs = con.execute(sql)
        data = curs.fetchall()
    return data


def serve_single_maturity(args: dict) -> dict:
    sql = select_maturity_in_one(args)
    with engine.connect() as con:
        curs = con.execute(sql)
        data = curs.fetchall()
    return data


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                           #
#                     Routes                                                #
#                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@api.route('/curve/maturity', methods=['GET'])
class SingleTimeSeries(Resource):
    @api.marshal_with(single_ts_model)
    @api.expect(single_ts_parser)
    @flask_praetorian.auth_required
    def get(self):
        """Access a single maturity"""
        args = single_ts_parser.parse_args()
        return count_data(serve_single_maturity(args))


@api.route('/curve', methods=['GET'])
class YieldCurve(Resource):
    @api.marshal_with(curve_model)
    @api.expect(curve_parser)
    @flask_praetorian.auth_required
    def get(self):
        """Get the full yield curve"""
        args = curve_parser.parse_args()
        return count_data(serve_curve(args))
