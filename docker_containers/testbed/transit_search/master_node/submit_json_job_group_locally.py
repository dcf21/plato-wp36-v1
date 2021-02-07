#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# submit_json_job_group_locally.py

"""
Locally run a group of tasks defined in a JSON file
"""

import itertools
import json
import logging
import os
import sys
from math import log10
from string import Template

import argparse
import numpy as np
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


def run_task_list(job_name, task_list, iterations):
    # Work out all the permutations of options we need to try
    parameter_values = []
    for item in iterations:
        if 'values' in item:
            parameter_values.append([eval(val) for val in item['values']])
        if 'linear_range' in item:
            parameter_values.append(np.linspace(eval(item['linear_range'][0]),
                                                eval(item['linear_range'][1]),
                                                eval(item['linear_range'][2])))
        if 'log_range' in item:
            parameter_values.append(np.logspace(log10(eval(item['log_range'][0])),
                                                log10(eval(item['log_range'][1])),
                                                eval(item['log_range'][2])))
    parameter_combinations = itertools.product(*parameter_values)

    # Create list of all the task descriptions in this grid of tasks
    task_descriptions = []
    for counter, grid_point in enumerate(parameter_combinations):
        item = json.dumps(task_list)
        template = Template(item)
        format_tokens = {
            "index": "{:06d}".format(counter)
        }
        for index, setting in enumerate(iterations):
            format_tokens[setting['name']] = grid_point[index]

        task_descriptions.append(
            json.loads(template.substitute(**format_tokens))
        )

    # Status update
    logging.info("Running group of tasks <{}>".format(job_name))

    # Run each task in turn
    for message in task_descriptions:
        for task in message:
            # Run requested job
            do_work(job_name=job_name, body=task)


if __name__ == "__main__":
    # Read command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tasks', default="json_jobs/earth_vs_snr.json", type=str,
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
    test_descriptor_json = open(args.tasks).read()
    test_descriptor = json.loads(test_descriptor_json)

    # Enter infinite loop of listening for RabbitMQ messages telling us to do work
    run_task_list(job_name=test_descriptor['test_name'],
                  task_list=test_descriptor['task_list'],
                  iterations=test_descriptor['iterations'])
