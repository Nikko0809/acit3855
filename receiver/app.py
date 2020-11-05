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

HEADERS = { "content-type": "application/json" }

with open('app_conf.yml', 'r') as f:
  app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
  log_config = yaml.safe_load(f.read())
  logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def order_request(body):

  logger.info("Received event order_request with a unique id of {}".format(body["user_id"]))

  client = KafkaClient(hosts="%s:%d" % (app_config["events"]["hostname"],
                              app_config["events"]["port"]))
  topic = client.topics[app_config["events"]["topic"]]
  producer = topic.get_sync_producer()

  msg = { "type": "order_request",
          "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
          "payload": body
  }

  msg_str = json.dumps(msg)
  producer.produce(msg_str.encode('utf-8'))

  logger.info("Returned event order_request response (ID: {}) with status code {}".format(body['user_id'], 201))

  return NoContent, 201

def accept_order_request(body):

  logger.info("Received event accept_order_request with a unique id of {}".format(body["courier_id"]))

  client = KafkaClient(hosts="%s:%d" % (app_config["events"]["hostname"],
                              app_config["events"]["port"]))
  topic = client.topics[app_config["events"]["topic"]]
  producer = topic.get_sync_producer()

  msg = { "type": "accept_order_request",
          "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
          "payload": body
  }

  msg_str = json.dumps(msg)
  producer.produce(msg_str.encode('utf-8'))

  logger.info("Returned event accept_order_request response (ID: {}) with status code {}".format(body['courier_id'], 201))

  return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
  app.run(port=8080)
