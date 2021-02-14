from sqlalchemy import Column, Integer, String

from db import Base


class MetricsData(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    building = Column(String(255))
    metric_type = Column(String(255))
    value = Column(Integer)
    unit = Column(String(31))

    def as_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
