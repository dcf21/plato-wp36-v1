#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# display_message_queue.py

"""
Display the contents of the RabbitMQ message queues
"""

import logging
import os

import argparse
import pika
from plato_wp36 import settings


def print_queues(broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
    connection = pika.BlockingConnection(pika.URLParameters(url=broker))
    channel = connection.channel()

    queue_object = channel.queue_declare(queue=queue)

    queue_len = queue_object.method.message_count
    logging.info("{:d} messages waiting".format(queue_len))

    def callback(ch, method, properties, body):
        logging.info("--> Received {}".format(body))

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)

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

    # Wait for messages
    print_queues()
