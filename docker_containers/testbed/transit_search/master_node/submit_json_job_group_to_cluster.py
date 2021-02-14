#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# submit_json_job_group_to_cluster.py

"""
Populate message queue with a group of tasks defined in a JSON file, which may include iterations.
"""

import json
import logging
import os

import argparse
from plato_wp36 import settings, task_iterator

# Read command-line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tasks', default="json_jobs/earth_vs_size.json", type=str,
                    dest='tasks', help='The JSON file listing the tasks we are to perform')

args = parser.parse_args()

# Set up logging
log_file_path = os.path.join(settings.settings['dataPath'], 'plato_wp36.log')
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    handlers=[
                        logging.FileHandler(log_file_path),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)
logger.info("Running tests <{}>".format(args.tasks))

# Extract list of the jobs we are to do
job_descriptor_json = open(args.tasks).read()
job_descriptor = json.loads(job_descriptor_json)

# Submit jobs into the RabbitMQ job queue
task_iterator.TaskIterator.submit_tasks_to_rabbitmq(job_descriptor=job_descriptor)
