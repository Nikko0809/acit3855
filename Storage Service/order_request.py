from sqlalchemy import Column, Float, String, DateTime, Integer
from base import Base
import datetime
import json

class OrderRequest(Base):
  """ Order Request """

  __tablename__ = "order_request"

  id = Column(Integer, primary_key=True)
  user_id = Column(String(250), nullable=False)
  order_id = Column(String(250), nullable=False)
  orders = Column(String(500), nullable=False)
  total = Column(Float, nullable=False)
  timestamp = Column(String(100), nullable=False)
  date_created = Column(DateTime, nullable=False)

  def __init__(self, user_id, order_id, orders, total, timestamp):
    """ Initializes Order Request """
    self.user_id = user_id
    self.order_id = order_id
    self.orders = orders
    self.total = total
    self.timestamp = timestamp
    self.date_created = datetime.datetime.now()
  
  def to_dict(self):
    """ Dictionary Representation of Order Request """
    dict = {}
    dict['id'] = self.id
    dict['user_id'] = self.user_id
    dict['order_id'] = self.order_id
    dict['orders'] = json.loads(self.orders)
    dict['total'] = self.total
    dict['timestamp'] = self.timestamp
    dict['date_created'] = self.date_created

    return dict