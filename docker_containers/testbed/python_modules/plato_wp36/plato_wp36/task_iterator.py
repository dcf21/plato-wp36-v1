# -*- coding: utf-8 -*-
# task_iterator.py

"""
Locally run a group of tasks defined in a JSON file, which may include iterations.
"""

import itertools
import json
import logging
from math import log10
from string import Template

import numpy as np
from plato_wp36 import task_runner


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
            item = json.dumps(task_list)
            template = Template(item)
            format_tokens = {
                "index": "{:06d}".format(counter)
            }
            for index, setting in enumerate(iterations):
                format_tokens[setting['name']] = grid_point[index]

            task_descriptions.append(
                {
                    'job_name': job_name,
                    'task_list': json.loads(template.substitute(**format_tokens))
                }
            )

        # Return list of task lists
        return task_descriptions

    @staticmethod
    def submit_tasks_to_rabbitmq(job_descriptor, broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
        """
        Populate message queue with a group of tasks defined in a JSON file, which may include iterations.

        :param job_descriptor:
            Job descriptor, with fields <job_name>, <task_list> and <iterations>.
        :type job_descriptor:
            dict
        """
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
        for message in task_descriptions:
            for task in message:
                json_message = json.dumps(task)
                logging.info("Sending message <{}>".format(json_message))
                channel.basic_publish(exchange='', routing_key=queue, body=json_message)

    @staticmethod
    def run_tasks_locally(job_descriptor):
        """
        Run a group of tasks defined in a JSON file, which may include iterations.

        :param job_descriptor:
            Job descriptor, with fields <job_name>, <task_list> and <iterations>.
        :type job_descriptor:
            dict
        """
        # Job name
        job_name = job_descriptor.get('job_name', 'untitled')

        # Expand iterations
        iteration_expander = TaskIterator()

        # Create list of all the job lists for the worker nodes
        task_descriptions = iteration_expander.expand_task_list(job_descriptor=job_descriptor)

        # Loop over tasks
        worker = task_runner.TaskRunner(results_target="logging")
        for message in task_descriptions:
            worker.do_work(job_name=message['job_name'], task_list=message['task_list'])
