import connexion
from connexion import NoContent
import requests
import json
import os.path
import yaml
import logging
import logging.config
import datetime
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
  print("In Test Environment")
  app_conf_file = "/config/app_conf.yml"
  log_conf_file = "/config/log_conf.yml"
else:
  print("In Dev Environment")
  app_conf_file = "app_conf.yml"
  log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
  app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(log_conf_file, 'r') as f:
  log_config = yaml.safe_load(f.read())
  logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)

logger.info("Log Conf File: %s" % log_conf_file)

def get_order_request(index):
  """ Get the order reading in history """

  hostname = "%s:%d" % (app_config["events"]["hostname"], 
  app_config["events"]["port"])
  client = KafkaClient(hosts=hostname)
  topic = client.topics[app_config["events"]["topic"]]

  # Here we reset the offset on start so that we retrieve
  # messages at the beginning of the message queue.
  # To prevent the for loop from blocking, we set the timeout to
  # 100ms. There is a risk that this loop never stops if the
  # index is large and messages are constantly being received!

  consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                       consumer_timeout_ms=500)

  logger.info("Retrieving Order at index %d" % index)

  orders = []
  
  for msg in consumer:
    msg_str = msg.value.decode('utf-8')
    msg = json.loads(msg_str)

    if msg["type"] == 'order_request':
      orders.append(msg)
  
  try:
    return orders[index]['payload'], 200
  except IndexError:
    logger.error("Could not find order at index %d" % index)
    return { "message": "Not Found" }, 404

def get_accept_order_request(index):
  """ Get the order reading in history """

  hostname = "%s:%d" % (app_config["events"]["hostname"], 
  app_config["events"]["port"])
  client = KafkaClient(hosts=hostname)
  topic = client.topics[app_config["events"]["topic"]]

  # Here we reset the offset on start so that we retrieve
  # messages at the beginning of the message queue.
  # To prevent the for loop from blocking, we set the timeout to
  # 100ms. There is a risk that this loop never stops if the
  # index is large and messages are constantly being received!

  consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                       consumer_timeout_ms=500)

  logger.info("Retrieving Accept Order at index %d" % index)

  orders = []
  
  for msg in consumer:
    msg_str = msg.value.decode('utf-8')
    msg = json.loads(msg_str)

    if msg["type"] == 'accept_order_request':
      orders.append(msg)

  try:
    return orders[index]['payload'], 200
  except IndexError:
    logger.error("Could not find accept order at index %d" % index)
    return { "message": "Not Found" }, 404

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", base_path="/audit_log", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
  app.run(port=8110)