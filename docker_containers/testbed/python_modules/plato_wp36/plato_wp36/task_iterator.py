# -*- coding: utf-8 -*-
# task_iterator.py

"""
Locally run a group of tasks defined in a JSON file, which may include iterations.
"""

import itertools
import json
import logging
import os
import time
import traceback
from math import log10
from string import Template

import numpy as np
import pika
from plato_wp36 import task_runner
from plato_wp36.results_logger import ResultsToRabbitMQ

# noinspection PyUnresolvedReferences
from .constants import *


class TaskIterator:
    """
    Expand a series of jobs, defined by a job description, which may include iterations. Return a list of task lists.
    """

    def __init__(self):
        """
        Instantiate a task runner.
        """
        pass

    def expand_task_list(self, job_descriptor: dict):
        """
        Expand a series of jobs, defined by a job description, which may include iterations. Return a list of task
        lists.

        :param job_descriptor:
            Dictionary describing a job we are to run, including iterations.
            Job descriptor, with fields <job_name>, <task_list> and <iterations>.
        :type job_descriptor:
            dict
        :return:
            list of task lists
        """

        # Define the null iteration we use over a single item, if none is provided
        null_iteration = [
            {
                'name': 'null',
                'values': [0]
            }
        ]

        # Extract job information from input data structure
        job_name = job_descriptor.get('job_name', 'untitled')
        clean_up = job_descriptor.get('clean_up', True)
        iterations = job_descriptor.get('iterations', null_iteration)
        task_list = job_descriptor.get('task_list', [])

        # Work out all the permutations of settings we need to iterate over
        parameter_values = []
        for item in iterations:
            if 'values' in item:
                parameter_values.append([eval(str(val)) for val in item['values']])
            if 'linear_range' in item:
                parameter_values.append(np.linspace(eval(str(item['linear_range'][0])),
                                                    eval(str(item['linear_range'][1])),
                                                    eval(str(item['linear_range'][2]))))
            if 'log_range' in item:
                parameter_values.append(np.logspace(log10(eval(str(item['log_range'][0]))),
                                                    log10(eval(str(item['log_range'][1]))),
                                                    eval(str(item['log_range'][2]))))
        parameter_combinations = itertools.product(*parameter_values)

        # Create list of all the task descriptions in this grid of tasks
        task_descriptions = []
        for counter, grid_point in enumerate(parameter_combinations):
            # Convert task list template into a JSON string
            item = json.dumps(task_list)
            template = Template(item)

            # Compile dictionary of iteration values
            format_tokens = {
                "index": "{:06d}".format(counter)
            }
            for index, setting in enumerate(iterations):
                format_tokens[setting['name']] = grid_point[index]

            # Substitute the iteration values into the task list
            task_list_item = json.loads(template.substitute(**format_tokens))

            # Create job for this particular permutation of iterator values
            task_descriptions.append(
                {
                    'job_name': job_name,
                    'job_parameters': format_tokens,
                    'clean_up': clean_up,
                    'task_list': task_list_item
                }
            )

        # Return list of task lists
        return task_descriptions

    @staticmethod
    def submit_tasks_to_rabbitmq(from_file=None, job_descriptor=None,
                                 broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
        """
        Populate message queue with a group of tasks defined in a JSON file, which may include iterations.

        :param from_file:
            Filename of JSON file from which we are to read a task list (optional).
        :type from_file:
            str
        :param job_descriptor:
            Job descriptor, with fields <job_name>, <task_list> and <iterations>.
        :type job_descriptor:
            dict
        """

        # If task list supplied as filename of JSON file, read it now
        if from_file is not None:
            job_descriptor_json = open(from_file).read()
            TaskIterator.submit_tasks_to_rabbitmq(job_descriptor=json.loads(job_descriptor_json),
                                                  broker=broker, queue=queue)
        if job_descriptor is None:
            return

        # Run any sub-jobs (allows JSON files to be nested)
        if 'nested_tasks' in job_descriptor:
            for subitem in job_descriptor['nested_tasks']:
                TaskIterator.submit_tasks_to_rabbitmq(
                    from_file=subitem,
                    broker=broker, queue=queue
                )

        # Job name
        job_name = job_descriptor.get('job_name', 'untitled')

        # Expand iterations
        iteration_expander = TaskIterator()

        # Create list of all the job lists for the worker nodes
        task_descriptions = iteration_expander.expand_task_list(job_descriptor=job_descriptor)

        # Now submit tasks to the message queue
        connection = pika.BlockingConnection(pika.URLParameters(url=broker))
        channel = connection.channel()

        channel.queue_declare(queue=queue)

        logging.info("Running group of tasks <{}>".format(job_name))

        # Loop over tasks
        for task in task_descriptions:
            json_message = json.dumps(task)
            logging.info("Sending message <{}>".format(json_message))
            channel.basic_publish(exchange='', routing_key=queue, body=json_message)

    @staticmethod
    def run_tasks_locally(from_file=None, job_descriptor=None):
        """
        Run a group of tasks defined in a JSON file, which may include iterations.

        :param from_file:
            Filename of JSON file from which we are to read a task list (optional).
        :type from_file:
            str
        :param job_descriptor:
            Job descriptor, with fields <job_name>, <task_list> and <iterations>.
        :type job_descriptor:
            dict
        """

        # If task list supplied as filename of JSON file, read it now
        if from_file is not None:
            job_descriptor_json = open(from_file).read()
            TaskIterator.run_tasks_locally(job_descriptor=json.loads(job_descriptor_json))
        if job_descriptor is None:
            return

        # Make sure we return to working directory after handling any exceptions
        cwd = os.getcwd()

        # Run any sub-jobs (allows JSON files to be nested)
        if 'nested_tasks' in job_descriptor:
            for subitem in job_descriptor['nested_tasks']:
                TaskIterator.run_tasks_locally(from_file=subitem)

        # Job name
        job_name = job_descriptor.get('job_name', 'untitled')

        # Expand iterations
        iteration_expander = TaskIterator()

        # Create list of all the job lists for the worker nodes
        task_descriptions = iteration_expander.expand_task_list(job_descriptor=job_descriptor)

        # Loop over tasks
        results_target = "logging"

        worker = task_runner.TaskRunner(results_target=results_target)
        for message in task_descriptions:
            try:
                worker.do_work(job_name=message.get('job_name', job_name),
                               job_parameters=job_descriptor.get('job_parameters', {}),
                               clean_up_products=job_descriptor.get('clean_up', True),
                               task_list=message['task_list'])
            except Exception:
                error_message = "\n\n\n !!!! \n\n\n{}".format(traceback.format_exc())
                result_log = ResultsToRabbitMQ(results_target=results_target)

                # File result to message queue
                result_log.record_result(job_name=message.get('job_name', job_name),
                                         parameters=job_descriptor.get('job_parameters', {}),
                                         task_name='error_message', timestamp=time.time(),
                                         result=error_message)
            finally:
                os.chdir(cwd)
