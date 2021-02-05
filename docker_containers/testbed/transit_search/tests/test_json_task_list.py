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


def do_work(job_name, body):
    """
    Perform a list of tasks sent to us via a JSON message

    :param job_name:
        The name of the test that this task is part of
    :type job_name:
        str
    :param body:
        List of dictionaries, describing the tasks to be performed.
    :type body:
        List[Dict]
    """

    # Do each task in list
    worker = task_runner.TaskRunner(results_target="logging")
    worker.do_work(job_name=job_name, task_list=body)


def run_task_list(job_name, task_list):
    """
    Run a sequence of jobs, one by one

    :param job_name:
        The name of the test that this task is part of
    :type job_name:
        str
    :param task_list:
        List of list of dictionaries, describing the tasks to be performed.
    :type task_list:
        List[List[Dict]]
    """
    logging.info('Running sequence of tasks')

    # Check that task list is a list
    assert isinstance(task_list, list)

    # Run each task in turn
    for message in task_list:
        # Run requested job
        do_work(job_name=job_name, body=message)


if __name__ == "__main__":
    # Read command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tasks', default="json/test_batman_synthesise_earth.json", type=str,
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
    test_descriptor_json = open(args.tasks).read()
    test_descriptor = json.loads(test_descriptor_json)

    # Enter infinite loop of listening for RabbitMQ messages telling us to do work
    run_task_list(job_name=test_descriptor['test_name'], task_list=test_descriptor['task_list'])
