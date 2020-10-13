#!../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# speed_test_worker_v2.py

"""
Run speed tests as requested through the RabbitMQ message queue

See:
https://stackoverflow.com/questions/14572020/handling-long-running-tasks-in-pika-rabbitmq/52951933#52951933
https://github.com/pika/pika/blob/0.12.0/examples/basic_consumer_threaded.py
"""

import argparse
import json
import logging
import os

import pika
from plato_wp36 import settings
from speed_test_worker_v1 import speed_test


def do_work(body):
    # Process lightcurve
    job_description = json.loads(body)
    speed_test(
        lc_duration=job_description['lc_duration'],
        tda_name=job_description['tda_name'],
        lc_filename=job_description['lc_filename']
    )


def receive(broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
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


def run_speed_tests(broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
    logging.info('Waiting for messages. To exit press CTRL+C')
    while True:
        # Fetch next message from queue
        message = receive(broker=broker, queue=queue)

        # If no message received quit
        if message is None:
            return

        # Run requested job
        do_work(body=message)


if __name__ == "__main__":
    # Read commandline arguments
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

    # Run speed tests
    run_speed_tests()
