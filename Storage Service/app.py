import connexion
from connexion import NoContent
import json
import os.path
import pymysql
import yaml
import datetime
import logging
import logging.config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from order_request import OrderRequest
from accept_order_request import AcceptOrderRequest
from pykafka import KafkaClient 
from pykafka.common import OffsetType 
from threading import Thread 

with open('app_conf.yml', 'r') as f:
  app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
  log_config = yaml.safe_load(f.read())
  logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

USER = app_config["datastore"]["user"]
PASSWORD = app_config["datastore"]["password"]
HOSTNAME = app_config["datastore"]["hostname"]
PORT = app_config["datastore"]["port"]
DB = app_config["datastore"]["db"]

DB_ENGINE = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(USER, PASSWORD, HOSTNAME, PORT, DB))
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info("Connecting to DB. Hostname:{}, Port:{}".format(HOSTNAME, PORT))

def get_order_request(timestamp):
  """ Gets order requests after timestamp """

  session = DB_SESSION()

  timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
  print(timestamp_datetime)

  readings = session.query(OrderRequest).filter(OrderRequest.date_created >= timestamp_datetime)

  results_list = [] 

  for reading in readings:
    results_list.append(reading.to_dict())
  
  session.close()

  logger.info("Query for Order Request after %s returns %d results" % (timestamp, len(results_list)))

  return results_list, 200

def order_request(body):
  """ Receives Order Request """

  session = DB_SESSION()

  order_req = OrderRequest(body['user_id'],
                            body['order_id'],
                            json.dumps(body['orders']),
                            body['total'],
                            body['timestamp'])
  
  session.add(order_req)

  session.commit()
  session.close()

  logger.debug("Stored event order_request with a unique id of {}".format(body['user_id']))

def get_accept_order_request(timestamp):
  """ Gets order requests after timestamp """

  session = DB_SESSION()

  timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
  print(timestamp_datetime)

  readings = session.query(AcceptOrderRequest).filter(AcceptOrderRequest.date_created >= timestamp_datetime)

  results_list = []

  for reading in readings:
    results_list.append(reading.to_dict())
  
  session.close()

  logger.info("Query for Order Request after %s returns %d results" % (timestamp, len(results_list)))

  return results_list, 200

def accept_order_request(body):
  """ Receives Accept Order Request """

  session = DB_SESSION()

  accept_order_req = AcceptOrderRequest(body['courier_id'],
                            body['order_id'],
                            json.dumps(body['orders']),
                            body['total'],
                            body['timestamp'])
  
  session.add(accept_order_req)

  session.commit()
  session.close()

  logger.debug("Stored event accept_order_request with a unique id of {}".format(body['courier_id']))

def process_messages():
  """ Process event messages """
  hostname = "%s:%d" % (app_config["events"]["hostname"],
                        app_config["events"]["port"])
  client = KafkaClient(hosts=hostname)
  topic = client.topics[app_config["events"]["topic"]]

  # Create a consume on a consumer group, that only reads new messages
  # (uncommitted messages) when the service re-starts (i.e., it doesn't
  # read all the old messages from the history in the message queue).
  consumer = topic.get_simple_consumer(consumer_group='event_group',
                                       reset_offset_on_start=False,
                                       auto_offset_reset=OffsetType.LATEST)
  # This is blocking - it will wait for a new message
  for msg in consumer:
    msg_str = msg.value.decode('utf-8')
    msg = json.loads(msg_str)
    logger.info("Message: %s" % msg)
    payload = msg["payload"]
    if msg["type"] == "order_request": # Change this to your event type
      # Store the event1 (i.e., the payload) to the DB
      order_request(payload)
    elif msg["type"] == "accept_order_request": # Change this to your event type
      # Store the event2 (i.e., the payload) to the DB
      accept_order_request(payload)
    # Commit the new message as being read
    consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
  t1 = Thread(target=process_messages)
  t1.setDaemon(True)
  t1.start()
  app.run(port=8090)
