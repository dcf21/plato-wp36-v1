#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# transit_search_worker_v2.py

"""
Run speed tests as requested through the RabbitMQ message queue

See:
https://stackoverflow.com/questions/14572020/handling-long-running-tasks-in-pika-rabbitmq/52951933#52951933
https://github.com/pika/pika/blob/0.12.0/examples/basic_consumer_threaded.py
"""

import functools
import json
import logging
import os
import time
import traceback

import argparse
import pika
from pika.exceptions import AMQPConnectionError
from plato_wp36 import settings, task_runner
from plato_wp36.results_logger import ResultsToRabbitMQ


def acknowledge_message(channel, delivery_tag):
    """
    Acknowledge receipt of a RabbitMQ message, thereby preventing it from being sent to other worker nodes.
    """
    channel.basic_ack(delivery_tag=delivery_tag)


def do_work(connection=None, channel=None, delivery_tag=None, body='[{"task":"null"}]'):
    """
    Perform a list of tasks sent to us via a RabbitMQ message
    """

    # Make sure we return to working directory after handling any exceptions
    cwd = os.getcwd()

    # Extract list of the jobs we are to do
    job_descriptor = json.loads(body)

    # Define results target
    results_target = "rabbitmq"

    # Instantiate worker
    worker = task_runner.TaskRunner(results_target=results_target)
    try:
        # Check that job description is a dictionary
        if not isinstance(job_descriptor, dict):
            bad_message = job_descriptor
            job_descriptor = {'job_name': 'untitled'}
            raise ValueError("Bad message was not a dictionary: <{}>".format(bad_message))

        # Do requested task
        worker.do_work(job_name=job_descriptor.get('job_name', 'untitled'),
                       job_parameters=job_descriptor.get('job_parameters', {}),
                       clean_up_products=job_descriptor.get('clean_up', True),
                       task_list=job_descriptor['task_list'],
                       )
    except Exception:
        error_message = traceback.format_exc()
        result_log = ResultsToRabbitMQ(results_target=results_target)

        # File result to message queue
        result_log.record_result(job_name=job_descriptor['job_name'],
                                 parameters=job_descriptor.get('job_parameters', {}),
                                 task_name='error_message', timestamp=time.time(),
                                 result=error_message)
    finally:
        os.chdir(cwd)

    # Acknowledge the message we've just processed
    if connection is not None:
        cb = functools.partial(acknowledge_message, channel, delivery_tag)
        connection.add_callback_threadsafe(cb)


def receive(broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
    """
    A very simple RabbitMQ consumer, which receives a simple task from the job queue, acknowledges it, and then
    closes the connection to RabbitMQ. This workflow prevents issues with the RabbitMQ connection dropping during
    long-running transit-search tasks.
    """
    connection = pika.BlockingConnection(pika.URLParameters(url=broker))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    method_frame, header_frame, body = channel.basic_get(queue=queue)
    if method_frame is None or method_frame.NAME == 'Basic.GetEmpty':
        connection.close()
        return None
    else:
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        connection.close()
        return body


def run_worker_tasks(broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
    """
    Set up a very simple RabbitMQ consumer to receive messages from the job queue, one by one
    """
    logging.info('Waiting for messages. To exit press CTRL+C')
    while True:
        # Fetch next message from queue
        try:
            message = receive(broker=broker, queue=queue)
        except AMQPConnectionError:
            logging.info("AMPQ connection failure")
            time.sleep(30)
            continue

        # If no message received then wait for work
        if message is None:
            time.sleep(10)
            continue

        # Run requested job
        do_work(body=message)


if __name__ == "__main__":
    # Read command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
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

    # Enter infinite loop of listening for RabbitMQ messages telling us to do work
    run_worker_tasks()
