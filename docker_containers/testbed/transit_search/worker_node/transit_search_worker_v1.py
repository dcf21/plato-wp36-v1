#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# transit_search_worker_v1.py

"""
Run speed tests as requested through the RabbitMQ message queue

This version receives all messages via a single connecion to the message queue, which is vulnerable to timing out

See:
https://stackoverflow.com/questions/14572020/handling-long-running-tasks-in-pika-rabbitmq/52951933#52951933
https://github.com/pika/pika/blob/0.12.0/examples/basic_consumer_threaded.py
"""

import functools
import json
import logging
import os
import threading
import time
import traceback

import argparse
import pika
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
                                 task_name='error', timestamp=time.time(),
                                 result=error_message)

    # Acknowledge the message we've just processed
    if connection is not None:
        cb = functools.partial(acknowledge_message, channel, delivery_tag)
        connection.add_callback_threadsafe(cb)


def message_callback(channel, method_frame, properties, body, args):
    """
    Callback function called by RabbitMQ when we receive a message telling us to do some work.
    """
    (connection, threads) = args

    logging.info("--> Received {}".format(body))

    delivery_tag = method_frame.delivery_tag

    t = threading.Thread(target=do_work, args=(connection, channel, delivery_tag, body))
    t.start()
    threads.append(t)


def run_transit_searches(broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
    """
    Set up a RabbitMQ consumer to call the <message_callback> function whenever we receive a message
    telling us to do some work.
    """
    connection = pika.BlockingConnection(pika.URLParameters(url=broker))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    channel.queue_declare(queue=queue)

    threads = []
    on_message_callback = functools.partial(message_callback, args=(connection, threads))
    channel.basic_consume(queue=queue, on_message_callback=on_message_callback)

    logging.info('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


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
    run_transit_searches()
