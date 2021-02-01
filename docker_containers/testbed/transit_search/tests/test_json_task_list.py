#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# test_json_task_list.py

"""
Test that test bench can perform the series of tasks defined in a JSON file
"""

import json
import logging
import os

import argparse
from plato_wp36 import settings, task_runner


def do_work(body):
    """
    Perform a list of tasks sent to us via a JSON message
    """

    # Do each task in list
    task_runner.do_work(task_list=body)


def run_task_list(task_list):
    """
    Run a sequence of jobs, one by one
    """
    logging.info('Running sequence of tasks')
    for message in task_list:
        # Run requested job
        do_work(body=message)


if __name__ == "__main__":
    # Read command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tasks', required=True, type=str,
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
    logger.info(__doc__.strip())

    # Extract list of the jobs we are to do
    task_list_text = open(args.tasks).read()
    task_list = json.loads(task_list_text)

    # Enter infinite loop of listening for RabbitMQ messages telling us to do work
    run_task_list(task_list=task_list)
