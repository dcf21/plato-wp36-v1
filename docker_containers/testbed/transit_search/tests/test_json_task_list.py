#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# test_json_task_list.py

"""
Test that test-bench can perform the series of tasks defined in a JSON file
"""

import logging
import os
import sys

import argparse
from plato_wp36 import settings, task_iterator

# Read command-line arguments
parser = argparse.ArgumentParser(description=__doc__)

# Filename for JSON descriptor of tests to run
parser.add_argument('--tasks', default="json/launchers/quick_tests.json", type=str,
                    dest='tasks', help='The JSON file listing the tasks we are to perform')

# Flush previous simultaneous detections?
parser.add_argument('--local', dest='local', action='store_true')
parser.add_argument('--cluster', dest='local', action='store_false')
parser.set_defaults(local=True)

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

if args.local:
    # Run jobs immediately
    task_iterator.TaskIterator.run_tasks_locally(from_file=args.tasks)
else:
    # Run jobs on Kubernetes cluster
    task_iterator.TaskIterator.submit_tasks_to_rabbitmq(from_file=args.tasks)
