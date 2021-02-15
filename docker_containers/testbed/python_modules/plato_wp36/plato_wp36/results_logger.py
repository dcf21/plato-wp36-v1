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

    def record_result(self, job_name, task_name, parameters, timestamp, result,
                      tda_code="", target_name="", result_extended=None):
        """
        Create a new entry in the message queue for transit detection results.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
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
        :param parameters:
            A dictionary of parameter values associated with this task.
        :type parameters:
            dict
        :param timestamp:
            The unix time stamp when this test was performed.
        :type timestamp:
            float
        :param result:
            Data structure containing the output from the TDA code
        :param result:
            Data structure containing the extended output from the TDA code (saved to disk)
        :return:
            None
        """

        # Convert results data structure to JSON
        result_json = json.dumps(result)
        json_filename = ""

        # Store extended results of this task as gzipped JSON output (if it's too big to fit in the database)
        if result_extended is not None:
            result_extended_directory = os.path.join(settings['dataPath'], "scratch")

            # Make sure directory exists for extended results files
            os.system("mkdir -p '{}'".format(result_extended_directory))

            # Create a filename for the extended results of this test
            json_filename = "{}_{}_{}_{}.json.gz".format(job_name,
                                                         task_name,
                                                         tda_code,
                                                         os.path.split(target_name)[1])
            json_out_path = os.path.join(result_extended_directory, json_filename)

            # Save extended results file
            with gzip.open(json_out_path, "wt") as f:
                f.write(json.dumps(result_extended))

        # Turn summarised result into a JSON string for storage in the database
        json_message = json.dumps({
            'job_name': job_name,
            'tda_code': tda_code,
            'target_name': target_name,
            'task_name': task_name,
            'parameters': parameters,
            'timestamp': timestamp,
            'result': result_json,
            'result_filename': json_filename
        })

        # Put this result in the queue to be saved in the database
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

            self.record_result(job_name=message['job_name'],
                               tda_code=message['tda_code'],
                               target_name=message['target_name'],
                               task_name=message['task_name'],
                               parameters=message['parameters'],
                               timestamp=message['timestamp'],
                               result=message['result'],
                               result_filename=message['result_filename']
                               )

        logging.info("Waiting for messages")
        channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()

    def record_result(self, job_name, tda_code, target_name, task_name, parameters, timestamp, result, result_filename):
        """
        Create a new entry in the database for a transit detection result.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
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
        :param parameters:
            A dictionary of parameter values associated with this task.
        :type parameters:
            dict
        :param timestamp:
            The unix time stamp when this test was performed.
        :type timestamp:
            float
        :param result:
            JSON string continue the result of this test
        :type result:
            str
        :param result_filename:
            The filename of the data structure containing the output from the TDA code, in the <scratch> directory
        :type result_filename:
            str
        :return:
            None
        """

        self.results_database.record_result(
            job_name=job_name,
            tda_code=tda_code,
            target_name=target_name,
            task_name=task_name,
            parameters=parameters,
            timestamp=timestamp,
            result=result,
            result_filename=result_filename
        )
