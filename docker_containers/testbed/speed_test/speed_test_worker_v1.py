#!../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# speed_test_worker.py

"""
Run speed tests as requested through the RabbitMQ message queue

This version receives all messages via a single connecion to the message queue, which is vulnerable to timing out

See:
https://stackoverflow.com/questions/14572020/handling-long-running-tasks-in-pika-rabbitmq/52951933#52951933
https://github.com/pika/pika/blob/0.12.0/examples/basic_consumer_threaded.py
"""

import argparse
import logging
import pika
import os
import functools
import json
import time
import threading

from plato_wp36 import lcsg_lc_reader, settings, results_logger, run_time_logger, task_timer
from plato_wp36.tda_wrappers import bls_reference, bls_kovacs, dst_v26, dst_v29, exotrans, qats, tls


def speed_test(lc_duration, tda_name, lc_filename):
    logging.info("Running <{lc_filename}> through <{tda_name}> with duration {lc_days:.1f}.".format(
        lc_filename=lc_filename,
        tda_name=tda_name,
        lc_days=lc_duration / 86400)
    )

    # Record start time
    start_time = time.time()

    # Open connections to transit results and run times to RabbitMQ message queues
    time_log = run_time_logger.RunTimesToRabbitMQ()
    result_log = results_logger.ResultsToRabbitMQ()

    # Load lightcurve
    with task_timer.TaskTimer(tda_code=tda_name, target_name=lc_filename, task_name='load_lc',
                              lc_length=lc_duration, time_logger=time_log):
        lc = lcsg_lc_reader.read_lcsg_lightcurve(
            filename=lc_filename,
            gzipped=True,
            cut_off_time=lc_duration / 86400
        )

    # Process lightcurve
    with task_timer.TaskTimer(tda_code=tda_name, target_name=lc_filename, task_name='transit_detection',
                              lc_length=lc_duration, time_logger=time_log):
        if tda_name == 'bls_reference':
            output = bls_reference.process_lightcurve(lc, lc_duration / 86400)
        elif tda_name == 'bls_kovacs':
            output = bls_kovacs.process_lightcurve(lc, lc_duration / 86400)
        elif tda_name == 'dst_v26':
            output = dst_v26.process_lightcurve(lc, lc_duration / 86400)
        elif tda_name == 'dst_v29':
            output = dst_v29.process_lightcurve(lc, lc_duration / 86400)
        elif tda_name == 'exotrans':
            output = exotrans.process_lightcurve(lc, lc_duration / 86400)
        elif tda_name == 'qats':
            output = qats.process_lightcurve(lc, lc_duration / 86400)
        elif tda_name == 'tls':
            output = tls.process_lightcurve(lc, lc_duration / 86400)
        else:
            assert False, "Unknown transit detection code <{}>".format(tda_name)

    # Send result to message queue
    result_log.record_result(tda_code=tda_name, target_name=lc_filename, task_name='transit_detection',
                             lc_length=lc_duration, timestamp=start_time,
                             result=output)

    # Close connection to message queue
    time_log.close()
    result_log.close()


def acknowledge_message(channel, delivery_tag):
    channel.basic_ack(delivery_tag=delivery_tag)


def do_work(connection, channel, delivery_tag, body):
    # Process lightcurve
    job_description = json.loads(body)
    speed_test(
        lc_duration=job_description['lc_duration'],
        tda_name=job_description['tda_name'],
        lc_filename=job_description['lc_filename']
    )

    # Acknowledge the message we've just processed
    cb = functools.partial(acknowledge_message, channel, delivery_tag)
    connection.add_callback_threadsafe(cb)

def message_callback(channel, method_frame, properties, body, args):
    (connection, threads) = args

    logging.info("--> Received {}".format(body))

    delivery_tag = method_frame.delivery_tag

    t = threading.Thread(target=do_work, args=(connection, channel, delivery_tag, body))
    t.start()
    threads.append(t)

def run_speed_tests(broker="amqp://guest:guest@rabbitmq-service:5672", queue="tasks"):
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
