#!../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# task_runner.py

"""
Run lightcurve processing tasks, as defined within request objects.
"""

import logging
import os
import time

from eas_batman_wrapper.batman_wrapper import BatmanWrapper
from eas_psls_wrapper.psls_wrapper import PslsWrapper

from .lc_reader_archive import read_archive_lightcurve
from .lc_reader_lcsg import read_lcsg_lightcurve
from .results_logger import ResultsToRabbitMQ
from .run_time_logger import RunTimesToRabbitMQ
from .task_timer import TaskTimer
from .tda_wrappers import bls_reference, bls_kovacs, dst_v26, dst_v29, exotrans, qats, tls


class TaskRunner:
    """
    Run lightcurve processing tasks, as defined within request objects.
    """

    def __init__(self, results_target="rabbitmq"):
        """
        Instantiate a task runner.

        :param results_target:
            Define where we send our results to
        :type results_target:
            str
        """
        self.results_target = results_target

    def psls_synthesise(self, job_name, lc_filename, lc_directory, lc_specs):
        """
        Perform the task of synthesising a lightcurve using PSLS.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param lc_filename:
            Filename to give the lightcurve we synthesise.
        :type lc_filename:
            str
        :param lc_directory:
            Directory to place the output lightcurve into.
        :type lc_directory:
            str
        :param lc_specs:
            Specifications for the lightcurve we are to synthesise. The dictionary should define the following keys:
            <duration>, <enable_transit>, <planet_radius>, <orbital_period>, <semi_major_axis>, <orbital_angle>
        :type lc_specs:
            dict
        """
        logging.info("Running PSLS synthesis")

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Do synthesis
        with TaskTimer(job_name=job_name, target_name=lc_filename, task_name='psls_synthesis', time_logger=time_log):
            synthesiser = PslsWrapper()
            synthesiser.configure(**lc_specs)
            synthesiser.synthesise(directory=lc_directory,
                                   filename=lc_filename,
                                   gzipped=True)
            synthesiser.close()

        # Close connection to message queue
        time_log.close()

    def batman_synthesise(self, job_name, lc_filename, lc_directory, lc_specs):
        """
        Perform the task of synthesising a lightcurve using batman.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param lc_filename:
            Filename to give the lightcurve we synthesise.
        :type lc_filename:
            str
        :param lc_directory:
            Directory to place the output lightcurve into.
        :type lc_directory:
            str
        :param lc_specs:
            Specifications for the lightcurve we are to synthesise. The dictionary should define the following keys:
            <duration>, <enable_transit>, <planet_radius>, <orbital_period>, <semi_major_axis>, <orbital_angle>
        :type lc_specs:
            dict
        """
        logging.info("Running Batman synthesis")

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Do synthesis
        with TaskTimer(job_name=job_name, target_name=lc_filename, task_name='load_lc', time_logger=time_log):
            synthesiser = BatmanWrapper()
            synthesiser.configure(**lc_specs)
            synthesiser.synthesise(directory=lc_directory,
                                   filename=lc_filename,
                                   gzipped=True)
            synthesiser.close()

        # Close connection to message queue
        time_log.close()

    def lightcurves_multiply(self, job_name, lc_source,
                             input_1_filename, input_1_directory,
                             input_2_filename, input_2_directory,
                             output_filename, output_directory):
        """
        Perform the task of multiplying two lightcurves together.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param lc_source:
            The name of the format this lightcurve is in. Either <archive> or <lcsg>, for default formats used either
            by the testbench code (archive), or the lightcurve stitching group.
        :type lc_source:
            str

        :param input_1_filename:
            Filename for the first lightcurve to multiply.
        :type input_1_filename:
            str
        :param input_1_directory:
            Directory for the first lightcurve to multiply.
        :type input_1_directory:
            str

        :param input_2_filename:
            Filename for the second lightcurve to multiply.
        :type input_2_filename:
            str
        :param input_2_directory:
            Directory for the second lightcurve to multiply.
        :type input_2_directory:
            str

        :param output_filename:
            Filename for storing the output of our multiplication.
        :type output_filename:
            str
        :param output_directory:
            Directory for storing the output of our multiplication.
        :type output_directory:
            str
        """
        logging.info("Multiplying lightcurves")

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Work out which lightcurve reader to use
        if lc_source == 'lcsg':
            lc_reader = read_lcsg_lightcurve
        elif lc_source == 'archive':
            lc_reader = read_archive_lightcurve
        else:
            raise ValueError("Unknown lightcurve source <{}>".format(lc_source))

        # Load lightcurve 1
        with TaskTimer(job_name=job_name,
                       target_name=input_1_filename, task_name='load_lc', time_logger=time_log):
            lc_1 = lc_reader(
                filename=input_1_filename,
                directory=input_1_directory,
                gzipped=True
            )

        # Load lightcurve 2
        with TaskTimer(job_name=job_name,
                       target_name=input_2_filename, task_name='load_lc', time_logger=time_log):
            lc_2 = lc_reader(
                filename=input_2_filename,
                directory=input_2_directory,
                gzipped=True
            )

        # Multiply lightcurves together
        with TaskTimer(job_name=job_name,
                       target_name=input_1_filename, task_name='multiplication', time_logger=time_log):
            result = lc_1 * lc_2

        # Store result
        with TaskTimer(job_name=job_name,
                       target_name=output_filename, task_name='write_output', time_logger=time_log):
            result.to_file(directory=output_directory,
                           filename=output_filename)

        # Close connection to message queue
        time_log.close()

    def verify_lightcurve(self, job_name, lc_filename, lc_directory, lc_source):
        """
        Perform the task of verifying a lightcurve.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param lc_filename:
            The filename of the lightcurve to search for transits (within our local lightcurve archive).
        :type lc_filename
            str
        :param lc_directory:
            The name of the directory inside the lightcurve archive where this lightcurve can be found.
        :type lc_directory:
            str
        :param lc_source:
            The name of the format this lightcurve is in. Either <archive> or <lcsg>, for default formats used either
            by the testbench code (archive), or the lightcurve stitching group.
        :type lc_source:
            str
        """
        logging.info("Verifying <{lc_filename}>.".format(lc_filename=lc_filename))

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Work out which lightcurve reader to use
        if lc_source == 'lcsg':
            lc_reader = read_lcsg_lightcurve
        elif lc_source == 'archive':
            lc_reader = read_archive_lightcurve
        else:
            raise ValueError("Unknown lightcurve source <{}>".format(lc_source))

        # Load lightcurve
        with TaskTimer(job_name=job_name, target_name=lc_filename, task_name='load_lc', time_logger=time_log):
            lc = lc_reader(
                filename=lc_filename,
                directory=lc_directory,
                gzipped=True
            )

        # Verify lightcurve
        with TaskTimer(job_name=job_name, target_name=lc_filename, task_name='verify', time_logger=time_log):
            display_name = os.path.split(lc_filename)[1]

            # Run first code for checking LCs
            error_count = lc.check_fixed_step(verbose=True, max_errors=4)

            if error_count == 0:
                logging.info("V1: Lightcurve <{}> has fixed step".format(display_name))
            else:
                logging.info(
                    "V1: Lightcurve <{}> doesn't have fixed step ({:d} errors)".format(display_name, error_count))

            # Run second code for checking LCs
            error_count = lc.check_fixed_step_v2(verbose=True, max_errors=4)

            if error_count == 0:
                logging.info("V2: Lightcurve <{}> has fixed step".format(display_name))
            else:
                logging.info(
                    "V2: Lightcurve <{}> doesn't have fixed step ({:d} errors)".format(display_name, error_count))

        # Close connection to message queue
        time_log.close()

    def transit_search(self, job_name, lc_duration, tda_name, lc_filename, lc_directory, lc_source):
        """
        Perform the task of running a lightcurve through a transit-detection algorithm.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param lc_duration:
            The maximum length of lightcurve to use; truncate the lightcurve after this period of time (days).
        :type lc_duration:
            float
        :param tda_name:
            The name of the transit detection code to use.
        :type tda_name:
            str
        :param lc_filename:
            The filename of the lightcurve to search for transits (within our local lightcurve archive).
        :type lc_filename
            str
        :param lc_directory:
            The name of the directory inside the lightcurve archive where this lightcurve can be found.
        :type lc_directory:
            str
        :param lc_source:
            The name of the format this lightcurve is in. Either <archive> or <lcsg>, for default formats used either
            by the testbench code (archive), or the lightcurve stitching group.
        :type lc_source:
            str
        """
        logging.info("Running <{lc_filename}> through <{tda_name}> with duration {lc_days:.1f}.".format(
            lc_filename=lc_filename,
            tda_name=tda_name,
            lc_days=lc_duration)
        )

        # Record start time
        start_time = time.time()

        # Work out which lightcurve reader to use
        if lc_source == 'lcsg':
            lc_reader = read_lcsg_lightcurve
        elif lc_source == 'archive':
            lc_reader = read_archive_lightcurve
        else:
            raise ValueError("Unknown lightcurve source <{}>".format(lc_source))

        # Open connections to transit results and run times to RabbitMQ message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)
        result_log = ResultsToRabbitMQ(results_target=self.results_target)

        # Load lightcurve
        with TaskTimer(job_name=job_name, tda_code=tda_name, target_name=lc_filename, task_name='load_lc',
                       lc_length=lc_duration, time_logger=time_log):
            lc = lc_reader(
                filename=lc_filename,
                directory=lc_directory,
                gzipped=True,
                cut_off_time=lc_duration
            )

        # Process lightcurve
        with TaskTimer(job_name=job_name, tda_code=tda_name, target_name=lc_filename, task_name='transit_detection',
                       lc_length=lc_duration, time_logger=time_log):
            if tda_name == 'bls_reference':
                output, output_extended = bls_reference.process_lightcurve(lc, lc_duration)
            elif tda_name == 'bls_kovacs':
                output, output_extended = bls_kovacs.process_lightcurve(lc, lc_duration)
            elif tda_name == 'dst_v26':
                output, output_extended = dst_v26.process_lightcurve(lc, lc_duration)
            elif tda_name == 'dst_v29':
                output, output_extended = dst_v29.process_lightcurve(lc, lc_duration)
            elif tda_name == 'exotrans':
                output, output_extended = exotrans.process_lightcurve(lc, lc_duration)
            elif tda_name == 'qats':
                output, output_extended = qats.process_lightcurve(lc, lc_duration)
            elif tda_name == 'tls':
                output, output_extended = tls.process_lightcurve(lc, lc_duration)
            else:
                assert False, "Unknown transit detection code <{}>".format(tda_name)

        # Send result to message queue
        result_log.record_result(job_name=job_name, tda_code=tda_name, target_name=lc_filename,
                                 task_name='transit_detection',
                                 lc_length=lc_duration, timestamp=start_time,
                                 result=output, result_extended=output_extended)

        # Close connection to message queue
        time_log.close()
        result_log.close()

    def do_work(self, task_list, job_name="not set"):
        """
        Perform a list of tasks sent to us via a list of request structures

        :param job_name:
            Optionally, specify the name of the job that these tasks are part of. If the "job_name" field is specified
            in the tasks, this overrides the job name specified here.
        :type job_name:
            str
        :param task_list:
            A list of dictionaries describing the tasks we are to perform, in sequence. Each task is assumed to depend
            on the previous tasks, and so they are not run in parallel.
        :type task_list:
            List
        """

        # Check that task list is a list
        assert isinstance(task_list, list)

        # Do each task in list
        for job_description in task_list:
            # Check that task description is a dictionary
            assert isinstance(job_description, dict)

            # If job name is not specified in the job description, we specify it here
            if 'job_name' not in job_description:
                job_description['job_name'] = job_name

            # Null task
            if job_description['task'] == 'null':
                logging.info("Running null task")

            # Transit search
            elif job_description['task'] == 'transit_search':
                self.transit_search(
                    job_name=job_description['job_name'],
                    lc_source=job_description['lc_source'],
                    lc_duration=job_description['lc_duration'],
                    lc_directory=job_description['lc_directory'],
                    tda_name=job_description['tda_name'],
                    lc_filename=job_description['lc_filename']
                )

            # Synthesise lightcurve with PSLS
            elif job_description['task'] == 'psls_synthesise':
                self.psls_synthesise(
                    job_name=job_description['job_name'],
                    lc_filename=job_description['lc_filename'],
                    lc_directory=job_description['lc_directory'],
                    lc_specs=job_description['lc_specs']
                )

            # Synthesise lightcurve with Batman
            elif job_description['task'] == 'batman_synthesise':
                self.batman_synthesise(
                    job_name=job_description['job_name'],
                    lc_filename=job_description['lc_filename'],
                    lc_directory=job_description['lc_directory'],
                    lc_specs=job_description['lc_specs']
                )

            # Multiply two lightcurves together
            elif job_description['task'] == 'multiplication':
                self.lightcurves_multiply(
                    job_name=job_description['job_name'],
                    lc_source=job_description['lc_source'],
                    input_1_filename=job_description['input_1_filename'],
                    input_1_directory=job_description['input_1_directory'],
                    input_2_filename=job_description['input_2_filename'],
                    input_2_directory=job_description['input_2_directory'],
                    output_filename=job_description['output_filename'],
                    output_directory=job_description['output_directory']
                )

            # Verify lightcurve
            elif job_description['task'] == 'verify_lc':
                self.verify_lightcurve(
                    job_name=job_description['job_name'],
                    lc_filename=job_description['lc_filename'],
                    lc_directory=job_description['lc_directory'],
                    lc_source=job_description['lc_source']
                )

            # Unknown task
            else:
                raise ValueError("Unknown task <{}>".format(job_description['task']))
