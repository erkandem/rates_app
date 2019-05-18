from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Float

Base = declarative_base()


class EuroYieldCurve(Base):
    """ """
    __tablename__ = 'euro_area_yield_curve'
    dt = Column(Date, primary_key=True)
    py_3m = Column(Float)
    py_4m = Column(Float)
    py_6m = Column(Float)
    py_9m = Column(Float)
    py_1y = Column(Float)
    py_2y = Column(Float)
    py_5y = Column(Float)
    py_7y = Column(Float)
    py_10y = Column(Float)
    py_15y = Column(Float)
    py_30y = Column(Float)

    def __init__(self, d: dict = None):
        if d is not None:
            self.__dict__.update(d)

    def init_from_dict(self, d: dict):
        self.__dict__.update(d)


