import connexion
from connexion import NoContent
import requests
import json
import os.path
import yaml
import datetime
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin
import os

HEADERS = {"content-type": "application/json"}

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

def populate_stats():
  """ Periodically update stats """
  logger.info("Start Periodic Processing")

  if (os.path.isfile(app_config["datastore"]["filename"])):
    with open(app_config["datastore"]["filename"], 'r') as f:
      stats = json.loads(f.read())
  else:
    stats = {
      "num_of_order_requests": 0,
      "total_of_order_requests": 0,
      "num_of_accept_order_requests": 0,
      "total_of_accept_order_requests": 0,
      "last_requested": "2019-01-01T01:00:00Z"
      # "last_requested": datetime.date.min.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

  order_response = requests.get(
    '{}/order-request'.format(app_config["eventstore"]["url"]),
    params={"timestamp": stats["last_requested"]}
    )
  accept_order_response = requests.get(
    '{}/accept-order-request'.format(app_config["eventstore"]["url"]),
    params={"timestamp": stats["last_requested"]}
    )

  current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

  if (order_response.status_code == 200 and accept_order_response.status_code == 200):
    logger.info("There are {} order request and {} accept order request received".format(
      len(order_response.json()), len(accept_order_response.json())))
  else:
    logger.error("There is an error on the response")

  total_of_order_requests = 0
  total_of_accept_order_requests = 0

  print(accept_order_response.json())

  for order in accept_order_response.json():
    total_of_accept_order_requests += order["total"]

  for order in order_response.json():
    total_of_order_requests += order["total"]

  stats['num_of_order_requests'] += len(order_response.json())
  stats['total_of_order_requests'] += round(total_of_order_requests, 2)
  stats['num_of_accept_order_requests'] += len(accept_order_response.json())
  stats['total_of_accept_order_requests'] += round(total_of_accept_order_requests, 2)
  stats['last_requested'] = current_time
  
  with open(app_config["datastore"]["filename"], 'w') as f:
    f.write(json.dumps(stats))

  logger.debug("Updated Stats: {}".format(json.dumps(stats)))
  
  logger.info("Periodic Processing has ended")


def init_scheduler():
  sched = BackgroundScheduler(daemon=True)
  sched.add_job(populate_stats,
                'interval',
                seconds=app_config['scheduler']['period_sec'])
  sched.start()


def get_stats():
  logger.info("Get Statistics request has started")

  if (os.path.isfile(app_config["datastore"]["filename"])):
    with open(app_config["datastore"]["filename"], 'r') as f:
      stats = json.loads(f.read())
  else:
    logger.error("Statistics does not exist")
    return "Statistics does not exist", 404
  
  logger.debug("Statistics: {}".format(stats))

  logger.info("Get Statistics request has ended")

  return stats, 200


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path="/processing", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
  init_scheduler()
  app.run(port=8100, use_reloader=False)
