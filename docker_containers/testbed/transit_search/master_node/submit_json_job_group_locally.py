#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# submit_json_job_group_locally.py

"""
Locally run a group of tasks defined in a JSON file
"""

import json
import logging
import os
import sys

import argparse
from plato_wp36 import settings, task_iterator

# Read command-line arguments
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tasks', default="json_jobs/earth_vs_size.json", type=str,
                    dest='tasks', help='The JSON file listing the tasks we are to perform')

args = parser.parse_args()


# Set up logging
class InfoFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno in (logging.DEBUG, logging.INFO)


h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(logging.DEBUG)
h1.addFilter(InfoFilter())
h2 = logging.StreamHandler()
h2.setLevel(logging.WARNING)

log_file_path = os.path.join(settings.settings['dataPath'], 'plato_wp36.log')
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    handlers=[
                        logging.FileHandler(log_file_path),
                        h1, h2
                    ])
logger = logging.getLogger(__name__)
logger.info("Running tests <{}>".format(args.tasks))

# Extract list of the jobs we are to do
job_descriptor_json = open(args.tasks).read()
job_descriptor = json.loads(job_descriptor_json)

# Run jobs immediately
task_iterator.TaskIterator.run_tasks_locally(job_descriptor=job_descriptor)
