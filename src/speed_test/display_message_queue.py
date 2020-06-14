#!../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# speed_test.py

"""
Display the contents of the RabbitMQ message queues
"""

import pika
import argparse
import os
import logging

from plato_wp36 import settings


def print_queues(broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
    channel = connection.channel()

    channel.queue_declare(queue=queue)

    def callback(ch, method, properties, body):
        logging.info("--> Received {}".format(body))

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)

    logging.info('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


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

    # Wait for messages
    print_queues()
