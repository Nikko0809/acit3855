from sqlalchemy import Column, Float, String, DateTime, Integer
from base import Base
import datetime
import json

class AcceptOrderRequest(Base):
  """ Accept Order Request """

  __tablename__ = "accept_order_request"

  id = Column(Integer, primary_key=True)
  courier_id = Column(String(250), nullable=False)
  order_id = Column(String(250), nullable=False)
  orders = Column(String(500), nullable=False)
  total = Column(Float, nullable=False)
  timestamp = Column(String(100), nullable=False)
  date_created = Column(DateTime, nullable=False)

  def __init__(self, courier_id, order_id, orders, total, timestamp):
    """ Initializes Accept Order Request """
    self.courier_id = courier_id
    self.order_id = order_id
    self.orders = orders
    self.total = total
    self.timestamp = timestamp
    self.date_created = datetime.datetime.now()
  
  def to_dict(self):
    """ Dictionary Representation of Accept Order Request """
    dict = {}
    dict['id'] = self.id
    dict['courier_id'] = self.courier_id
    dict['order_id'] = self.order_id
    dict['orders'] = json.loads(self.orders)
    dict['total'] = self.total
    dict['timestamp'] = self.timestamp
    dict['date_created'] = self.date_created

    return dict