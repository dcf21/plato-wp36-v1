# -*- coding: utf-8 -*-
# results_logger.py

import gzip
import json
import logging
import os

import pika

from .results_database import ResultsDatabase
from .settings import settings

"""
Provides a class used for compiling a database of the output from TDA codes.
"""


class ResultsToRabbitMQ:
    """
    Provides a class passing the results of various tasks to a RabbitMQ message queue.
    """

    def __init__(self,
                 broker="amqp://guest:guest@rabbitmq-service:5672",
                 queue="results",
                 results_target="rabbitmq"):
        """
        Open a handle to the message queue we send job results to.

        :param broker:
            The URL of the RabbitMQ broker we should send output to.
        :param queue:
            The name of the message queue we feed output into.
        """
        self.broker = broker
        self.queue = queue
        self.results_target = results_target

    def record_result(self, tda_code, target_name, task_name, lc_length, timestamp, result):
        """
        Create a new entry in the message queue for transit detection results.

        :param tda_code:
            The name of the Transit Detection Algorithm being used.
        :type tda_code:
            str
        :param target_name:
            The name of the target / lightcurve being analysed.
        :type target_name:
            str
        :param task_name:
            The name of the processing step being performed on the lightcurve.
        :type task_name:
            str
        :param lc_length:
            The length of the lightcurve (seconds)
        :type lc_length:
            float
        :param timestamp:
            The unix time stamp when this test was performed.
        :type timestamp:
            float
        :param result:
            Data structure containing the output from the TDA code
        :return:
            None
        """

        # Convert results data structure to JSON
        result_json = json.dumps(result)

        # Store a copy of this gzipped JSON output
        json_filename = "{}_{}_{}_{:08.1f}.json.gz".format(task_name,
                                                           tda_code,
                                                           os.path.split(target_name)[1],
                                                           lc_length / 86400)
        json_out_path = os.path.join(settings['dataPath'], "scratch", json_filename)
        with gzip.open(json_out_path, "wt") as f:
            f.write(result_json)

        json_message = json.dumps({
            'tda_code': tda_code,
            'target_name': target_name,
            'task_name': task_name,
            'lc_length': lc_length,
            'timestamp': timestamp,
            'result_filename': json_filename
        })

        if self.results_target == "rabbitmq":
            connection = pika.BlockingConnection(pika.URLParameters(url=self.broker))
            channel = connection.channel()
            channel.queue_declare(queue=self.queue)

            channel.basic_publish(exchange='', routing_key=self.queue, body=json_message)

            channel.close()
        elif self.results_target == "logging":
            logging.info(json_message)
        else:
            logging.info("Unknown target for results <{}>".format(self.results_target))

    def close(self):
        """
        Close connection to the RabbitMQ message queue.

        :return:
            None
        """

        pass


class ResultsToMySQL:
    """
    Provides a class passing the results of various tasks to a MySQL database.
    """

    def __init__(self, results_database=None):
        """
        Open a handle to the database we are to send results to.

        :param results_database:
            The class we use to communicate with the MySQL database
        """

        if results_database is None:
            results_database = ResultsDatabase()

        self.results_database = results_database

    def read_from_rabbitmq(self, broker="amqp://guest:guest@rabbitmq-service:5672", queue="results"):
        """
        Blocking call to read messages from RabbitMQ and send them to MySQL.

        :param broker:
            The URL of the RabbitMQ broker we should send output to.
        :param queue:
            The name of the message queue we feed output into.
        """
        broker = broker
        queue = queue

        connection = pika.BlockingConnection(pika.URLParameters(url=broker))
        channel = connection.channel()
        channel.queue_declare(queue=queue)

        def callback(ch, method, properties, body):
            logging.info("Received run time message <{}>".format(body))

            message = json.loads(body)

            self.record_result(tda_code=message['tda_code'],
                               target_name=message['target_name'],
                               task_name=message['task_name'],
                               lc_length=message['lc_length'],
                               timestamp=message['timestamp'],
                               result_filename=message['result_filename']
                               )

        logging.info("Waiting for messages")
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    def record_result(self, tda_code, target_name, task_name, lc_length, timestamp, result_filename):
        """
        Create a new entry in the database for a transit detection result.

        :param tda_code:
            The name of the Transit Detection Algorithm being used.
        :type tda_code:
            str
        :param target_name:
            The name of the target / lightcurve being analysed.
        :type target_name:
            str
        :param task_name:
            The name of the processing step being performed on the lightcurve.
        :type task_name:
            str
        :param lc_length:
            The length of the lightcurve (seconds)
        :type lc_length:
            float
        :param timestamp:
            The unix time stamp when this test was performed.
        :type timestamp:
            float
        :param result_filename:
            The filename of the data structure containing the output from the TDA code, in the <scratch> directory
        :type result_filename:
            str
        :return:
            None
        """

        self.results_database.record_result(
            tda_code=tda_code,
            target_name=target_name,
            task_name=task_name,
            lc_length=lc_length,
            timestamp=timestamp,
            result_filename=result_filename
        )
