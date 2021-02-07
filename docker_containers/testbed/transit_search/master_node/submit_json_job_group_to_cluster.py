#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# submit_json_job_group_to_cluster.py

"""
Populate message queue with a group of tasks defined in a JSON file
"""

import itertools
import json
import logging
import os
from math import log10
from string import Template

import argparse
import numpy as np
import pika
from plato_wp36 import settings


def run_task_list(job_name, task_list, iterations,
                  broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
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

    # Now submit tasks to the message queue
    connection = pika.BlockingConnection(pika.URLParameters(url=broker))
    channel = connection.channel()

    channel.queue_declare(queue=queue)

    logging.info("Running group of tasks <{}>".format(job_name))

    # Loop over tasks
    for message in task_descriptions:
        json_message = json.dumps(message)

        logging.info("Sending message <{}>".format(json_message))
        channel.basic_publish(exchange='', routing_key=queue, body=json_message)


if __name__ == "__main__":
    # Read command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tasks', default="json_jobs/tls_speed_test.json", type=str,
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
    test_descriptor_json = open(args.tasks).read()
    test_descriptor = json.loads(test_descriptor_json)

    # Enter infinite loop of listening for RabbitMQ messages telling us to do work
    run_task_list(job_name=test_descriptor['test_name'],
                  task_list=test_descriptor['task_list'],
                  iterations=test_descriptor['iterations'])
