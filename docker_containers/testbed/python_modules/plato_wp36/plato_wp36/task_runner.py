#!../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# task_runner.py

"""
Run lightcurve processing tasks, as defined within request objects
"""

import logging
import os
import time

import lc_reader_lcsg, lc_reader_psls, results_logger, run_time_logger, task_timer
from tda_wrappers import bls_reference, bls_kovacs, dst_v26, dst_v29, exotrans, qats, tls


def psls_synthesise(lc_filename, lc_directory, lc_specs):
    """
    Perform the task of synthesising a lightcurve using PSLS.
    """
    logging.info("Running PSLS synthesis")


def verify_lightcurve(lc_filename, lc_directory, lc_source):
    """
    Perform the task of verifying a lightcurve.
    """
    logging.info("Verifying <{lc_filename}>.".format(lc_filename=lc_filename))

    # Work out which lightcurve reader to use
    if lc_source == 'lcsg':
        lc_reader = lc_reader_lcsg.read_lcsg_lightcurve
    elif lc_source == 'psls':
        lc_reader = lc_reader_psls.read_psls_lightcurve
    else:
        raise ValueError("Unknown lightcurve source <{}>".format(lc_source))

    # Open connections to transit results and run times to RabbitMQ message queues
    time_log = run_time_logger.RunTimesToRabbitMQ()

    # Load lightcurve
    with task_timer.TaskTimer(target_name=lc_filename, task_name='verify_lc', time_logger=time_log):
        lc = lc_reader(
            filename=lc_filename,
            directory=lc_directory,
            gzipped=True
        )

    # Verify lightcurve
    display_name = os.path.split(lc_filename)[1]

    # Run first code for checking LCs
    error_count = lc.check_fixed_step(verbose=True, max_errors=4)

    if error_count == 0:
        logging.info("V1: Lightcurve <{}> has fixed step".format(display_name))
    else:
        logging.info("V1: Lightcurve <{}> doesn't have fixed step ({:d} errors)".format(display_name, error_count))

    # Run second code for checking LCs
    error_count = lc.check_fixed_step_v2(verbose=True, max_errors=4)

    if error_count == 0:
        logging.info("V2: Lightcurve <{}> has fixed step".format(display_name))
    else:
        logging.info("V2: Lightcurve <{}> doesn't have fixed step ({:d} errors)".format(display_name, error_count))

    # Close connection to message queue
    time_log.close()


def transit_search(lc_duration, tda_name, lc_filename, lc_directory, lc_source):
    """
    Perform the task of running a lightcurve through a transit-detection algorithm.
    """
    logging.info("Running <{lc_filename}> through <{tda_name}> with duration {lc_days:.1f}.".format(
        lc_filename=lc_filename,
        tda_name=tda_name,
        lc_days=lc_duration / 86400)
    )

    # Record start time
    start_time = time.time()

    # Work out which lightcurve reader to use
    if lc_source == 'lcsg':
        lc_reader = lc_reader_lcsg.read_lcsg_lightcurve
    elif lc_source == 'psls':
        lc_reader = lc_reader_psls.read_psls_lightcurve
    else:
        raise ValueError("Unknown lightcurve source <{}>".format(lc_source))

    # Open connections to transit results and run times to RabbitMQ message queues
    time_log = run_time_logger.RunTimesToRabbitMQ()
    result_log = results_logger.ResultsToRabbitMQ()

    # Load lightcurve
    with task_timer.TaskTimer(tda_code=tda_name, target_name=lc_filename, task_name='load_lc',
                              lc_length=lc_duration, time_logger=time_log):
        lc = lc_reader(
            filename=lc_filename,
            directory=lc_directory,
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
    """
    Acknowledge receipt of a RabbitMQ message, thereby preventing it from being sent to other worker nodes.
    """
    channel.basic_ack(delivery_tag=delivery_tag)


def do_work(task_list):
    """
    Perform a list of tasks sent to us via a list of request structures
    """

    # Do each task in list
    for job_description in task_list:
        if job_description['task'] == 'null':
            logging.info("Running null task")
        elif job_description['task'] == 'transit_search':
            transit_search(
                lc_source=job_description['lc_source'],
                lc_duration=job_description['lc_duration'],
                lc_directory=job_description['lc_directory'],
                tda_name=job_description['tda_name'],
                lc_filename=job_description['lc_filename']
            )
        elif job_description['task'] == 'psls_synthesise':
            psls_synthesise(
                lc_filename=job_description['lc_filename'],
                lc_directory=job_description['lc_directory'],
                lc_specs=job_description['lc_specs']

            )
        elif job_description['task'] == 'verify_lc':
            verify_lightcurve(
                lc_filename=job_description['lc_filename'],
                lc_directory=job_description['lc_directory'],
                lc_source=job_description['lc_source']
            )
        else:
            raise ValueError("Unknown task <{}>".format(job_description['task']))
