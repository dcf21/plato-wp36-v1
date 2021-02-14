# -*- coding: utf-8 -*-
# task_runner.py

"""
Run lightcurve processing tasks, as defined within a list of request objects.
"""

import logging
import os
import time

import numpy as np
from eas_batman_wrapper.batman_wrapper import BatmanWrapper
from eas_psls_wrapper.psls_wrapper import PslsWrapper

from .lc_reader_lcsg import read_lcsg_lightcurve
from .lightcurve import LightcurveArbitraryRaster
from .quality_control import quality_control
from .results_logger import ResultsToRabbitMQ
from .run_time_logger import RunTimesToRabbitMQ
from .task_timer import TaskTimer
from .tda_wrappers import bls_reference, bls_kovacs, dst_v26, dst_v29, exotrans, qats, tls


class TaskRunner:
    """
    Within a worker node, run a sequence of lightcurve processing tasks, as defined within a list of tasks.
    """

    def __init__(self, results_target="rabbitmq"):
        """
        Instantiate a task runner.

        :param results_target:
            Define where we send our results to
        :type results_target:
            str
        """

        # Destination for results from this task running. Either <rabbitmq> or <logging>
        self.results_target = results_target

        # List of all the lightcurves this task runner has written. Each a dictionary of <lc_filename> and
        # <lc_directory>
        self.lightcurves_written = []

        # In memory storage for lightcurve objects, by name
        self.lightcurves_in_memory = {}

    def psls_synthesise(self, job_name, lc_target, lc_filename, lc_directory, lc_specs):
        """
        Perform the task of synthesising a lightcurve using PSLS.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param lc_target:
            Specify whether this lightcurve is to be stored in <memory> or <archive>
        :type lc_target:
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
            lc_object = synthesiser.synthesise()
            synthesiser.close()

        # Write output
        if lc_target == "archive":
            with TaskTimer(job_name=job_name, target_name=lc_filename, task_name='write_lc', time_logger=time_log):
                lc.to_file(directory=lc_directory, filename=lc_filename)
                self.lightcurves_written.append({
                    'filename': lc_filename,
                    'directory': lc_directory
                })
        else:
            self.lightcurves_in_memory[lc_filename] = lc_object

        # Close connection to message queue
        time_log.close()

    def batman_synthesise(self, job_name, lc_target, lc_filename, lc_directory, lc_specs):
        """
        Perform the task of synthesising a lightcurve using batman.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param lc_target:
            Specify whether this lightcurve is to be stored in <memory> or <archive>
        :type lc_target:
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
            lc_object = synthesiser.synthesise()
            synthesiser.close()

        # Write output
        if lc_target == "archive":
            with TaskTimer(job_name=job_name, target_name=lc_filename, task_name='write_lc', time_logger=time_log):
                lc.to_file(directory=lc_directory, filename=lc_filename)
                self.lightcurves_written.append({
                    'filename': lc_filename,
                    'directory': lc_directory
                })
        else:
            self.lightcurves_in_memory[lc_filename] = lc_object

        # Close connection to message queue
        time_log.close()

    def lightcurves_multiply(self, job_name,
                             input_1_filename, input_1_directory, input_1_source,
                             input_2_filename, input_2_directory, input_2_source,
                             output_filename, output_directory, output_target):
        """
        Perform the task of multiplying two lightcurves together.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str

        :param input_1_filename:
            Filename for the first lightcurve to multiply.
        :type input_1_filename:
            str
        :param input_1_directory:
            Directory for the first lightcurve to multiply.
        :type input_1_directory:
            str
        :param input_1_source:
            Specify whether this lightcurve is stored in <memory>, <archive>, or <lcsg>
        :type input_1_source:
            str

        :param input_2_filename:
            Filename for the second lightcurve to multiply.
        :type input_2_filename:
            str
        :param input_2_directory:
            Directory for the second lightcurve to multiply.
        :type input_2_directory:
            str
        :param input_2_source:
            Specify whether this lightcurve is stored in <memory>, <archive>, or <lcsg>
        :type input_2_source:
            str

        :param output_filename:
            Filename for storing the output of our multiplication.
        :type output_filename:
            str
        :param output_directory:
            Directory for storing the output of our multiplication.
        :type output_directory:
            str
        :param output_target:
            Specify whether this lightcurve is to be stored in <memory> or <archive>
        :type output_target:
            str
        """
        logging.info("Multiplying lightcurves")

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Load lightcurve 1
        if input_1_source == 'memory':
            lc_1 = self.lightcurves_in_memory[input_1_filename]
        else:
            if input_1_source == 'lcsg':
                lc_reader = read_lcsg_lightcurve
            elif input_1_source == 'archive':
                lc_reader = LightcurveArbitraryRaster.from_file
            else:
                raise ValueError("Unknown lightcurve source <{}>".format(input_1_source))

            # Load lightcurve 1
            with TaskTimer(job_name=job_name,
                           target_name=input_1_filename, task_name='load_lc', time_logger=time_log):
                lc_1 = lc_reader(
                    filename=input_1_filename,
                    directory=input_1_directory
                )

        # Load lightcurve 2
        if input_2_source == 'memory':
            lc_2 = self.lightcurves_in_memory[input_2_filename]
        else:
            if input_2_source == 'lcsg':
                lc_reader = read_lcsg_lightcurve
            elif input_2_source == 'archive':
                lc_reader = LightcurveArbitraryRaster.from_file
            else:
                raise ValueError("Unknown lightcurve source <{}>".format(input_2_source))

            # Load lightcurve 2
            with TaskTimer(job_name=job_name,
                           target_name=input_2_filename, task_name='load_lc', time_logger=time_log):
                lc_2 = lc_reader(
                    filename=input_2_filename,
                    directory=input_2_directory
                )

        # Multiply lightcurves together
        with TaskTimer(job_name=job_name,
                       target_name=input_1_filename, task_name='multiplication', time_logger=time_log):
            result = lc_1 * lc_2

        # Store result
        if output_target == 'archive':
            with TaskTimer(job_name=job_name,
                           target_name=output_filename, task_name='write_output', time_logger=time_log):
                result.to_file(directory=output_directory,
                               filename=output_filename)
                self.lightcurves_written.append({
                    'filename': output_filename,
                    'directory': output_directory
                })
        elif output_target == "memory":
            self.lightcurves_in_memory[output_filename] = result
        else:
            raise ValueError("Unknown lightcurve target <{}>".format(output_target))

        # Close connection to message queue
        time_log.close()

    def verify_lightcurve(self, job_name, lc_filename, lc_directory, lc_source):
        """
        Perform the task of verifying a lightcurve.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param lc_target:
            Specify whether this lightcurve is stored in <memory> or <archive>
        :type lc_target:
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
            Specify whether this lightcurve is stored in <memory>, <archive>, or <lcsg>
        :type lc_source:
            str
        """
        logging.info("Verifying <{lc_filename}>.".format(lc_filename=lc_filename))

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Read input lightcurve
        if lc_source == 'memory':
            lc = self.lightcurves_in_memory[lc_filename]
        else:
            if lc_source == 'lcsg':
                lc_reader = read_lcsg_lightcurve
            elif lc_source == 'archive':
                lc_reader = LightcurveArbitraryRaster.from_file
            else:
                raise ValueError("Unknown lightcurve source <{}>".format(lc_source))

            # Load lightcurve
            with TaskTimer(job_name=job_name, target_name=lc_filename, task_name='load_lc', time_logger=time_log):
                lc = lc_reader(
                    filename=lc_filename,
                    directory=lc_directory
                )

        # Verify lightcurve
        with TaskTimer(job_name=job_name, target_name=lc_filename, task_name='verify', time_logger=time_log):
            display_name = os.path.split(lc_filename)[1]

            logging.info("Lightcurve <{}> time span {:.1f} to {:.1f}".format(display_name,
                                                                             np.min(lc.times),
                                                                             np.max(lc.times)))

            logging.info("Lightcurve <{}> flux range {:.6f} to {:.6f}".format(display_name,
                                                                              np.min(lc.fluxes),
                                                                              np.max(lc.fluxes)))

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

    def transit_search(self, job_name, lc_duration, tda_name,
                       lc_filename, lc_directory, lc_source, search_settings):
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
        :type lc_filename:
            str
        :param lc_directory:
            The name of the directory inside the lightcurve archive where this lightcurve can be found.
        :type lc_directory:
            str
        :param lc_source:
            Specify whether this lightcurve is stored in <memory>, <archive>, or <lcsg>
        :type lc_source:
            str
        :param search_settings:
            Dictionary of settings which control how we search for transits.
        :type search_settings:
            dict
        """
        logging.info("Running <{lc_filename}> through <{tda_name}> with duration {lc_days:.1f}.".format(
            lc_filename=lc_filename,
            tda_name=tda_name,
            lc_days=lc_duration)
        )

        # Record start time
        start_time = time.time()

        # Open connections to transit results and run times to RabbitMQ message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)
        result_log = ResultsToRabbitMQ(results_target=self.results_target)

        # Read input lightcurve
        if lc_source == 'memory':
            lc = self.lightcurves_in_memory[lc_filename]
        else:
            if lc_source == 'lcsg':
                lc_reader = read_lcsg_lightcurve
            elif lc_source == 'archive':
                lc_reader = LightcurveArbitraryRaster.from_file
            else:
                raise ValueError("Unknown lightcurve source <{}>".format(lc_source))

            # Load lightcurve
            with TaskTimer(job_name=job_name, target_name=lc_filename, task_name='load_lc', time_logger=time_log):
                lc = lc_reader(
                    filename=lc_filename,
                    directory=lc_directory
                )

        # Process lightcurve
        with TaskTimer(job_name=job_name, tda_code=tda_name, target_name=lc_filename, task_name='transit_detection',
                       lc_length=lc_duration, time_logger=time_log):
            if tda_name == 'bls_reference':
                output, output_extended = bls_reference.process_lightcurve(lc=lc, lc_duration=lc_duration,
                                                                           search_settings=search_settings)
            elif tda_name == 'bls_kovacs':
                output, output_extended = bls_kovacs.process_lightcurve(lc=lc, lc_duration=lc_duration,
                                                                        search_settings=search_settings)
            elif tda_name == 'dst_v26':
                output, output_extended = dst_v26.process_lightcurve(lc=lc, lc_duration=lc_duration,
                                                                     search_settings=search_settings)
            elif tda_name == 'dst_v29':
                output, output_extended = dst_v29.process_lightcurve(lc=lc, lc_duration=lc_duration,
                                                                     search_settings=search_settings)
            elif tda_name == 'exotrans':
                output, output_extended = exotrans.process_lightcurve(lc=lc, lc_duration=lc_duration,
                                                                      search_settings=search_settings)
            elif tda_name == 'qats':
                output, output_extended = qats.process_lightcurve(lc=lc, lc_duration=lc_duration,
                                                                  search_settings=search_settings)
            elif tda_name == 'tls':
                output, output_extended = tls.process_lightcurve(lc=lc, lc_duration=lc_duration,
                                                                 search_settings=search_settings)
            else:
                assert False, "Unknown transit detection code <{}>".format(tda_name)

        # Test whether transit detection was successful
        quality_control(lc=lc, metadata=output)

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

            # Null task
            if job_description['task'] == 'null':
                logging.info("Running null task")

            # Error task
            elif job_description['task'] == 'error':
                logging.info("Running error task")
                assert False, "Running error task"

            # Transit search
            elif job_description['task'] == 'transit_search':
                self.transit_search(
                    job_name=job_description.get('job_name', job_name),
                    lc_source=job_description.get('lc_source', 'memory'),
                    lc_duration=float(job_description.get('lc_duration', 730)),
                    lc_directory=job_description.get('lc_directory', 'test_output'),
                    tda_name=job_description.get('tda_name', 'tls'),
                    lc_filename=job_description.get('lc_filename', 'lightcurve'),
                    search_settings=job_description.get('search_settings', {})
                )

            # Synthesise lightcurve with PSLS
            elif job_description['task'] == 'psls_synthesise':
                self.psls_synthesise(
                    job_name=job_description.get('job_name', job_name),
                    lc_target=job_description.get('lc_target', 'memory'),
                    lc_filename=job_description.get('lc_filename', 'lightcurve'),
                    lc_directory=job_description.get('lc_directory', 'test_output'),
                    lc_specs=job_description.get('lc_specs', {})
                )

            # Synthesise lightcurve with Batman
            elif job_description['task'] == 'batman_synthesise':
                self.batman_synthesise(
                    job_name=job_description.get('job_name', job_name),
                    lc_target=job_description.get('lc_target', 'memory'),
                    lc_filename=job_description.get('lc_filename', 'lightcurve'),
                    lc_directory=job_description.get('lc_directory', 'test_output'),
                    lc_specs=job_description.get('lc_specs', {})
                )

            # Multiply two lightcurves together
            elif job_description['task'] == 'multiplication':
                self.lightcurves_multiply(
                    job_name=job_description.get('job_name', job_name),
                    input_1_filename=job_description['input_1_filename'],
                    input_1_directory=job_description.get('input_1_directory', 'test_output'),
                    input_1_source=job_description.get('input_1_target', 'memory'),
                    input_2_filename=job_description['input_2_filename'],
                    input_2_directory=job_description.get('input_2_directory', 'test_output'),
                    input_2_source=job_description.get('input_2_target', 'memory'),
                    output_filename=job_description['output_filename'],
                    output_directory=job_description.get('output_directory', 'test_output'),
                    output_target=job_description.get('output_target', 'memory')
                )

            # Verify lightcurve
            elif job_description['task'] == 'verify_lc':
                self.verify_lightcurve(
                    job_name=job_description.get('job_name', job_name),
                    lc_filename=job_description['lc_filename'],
                    lc_directory=job_description.get('lc_directory', 'test_output'),
                    lc_source=job_description.get('lc_source', 'memory')
                )

            # Unknown task
            else:
                raise ValueError("Unknown task <{}>".format(job_description['task']))
