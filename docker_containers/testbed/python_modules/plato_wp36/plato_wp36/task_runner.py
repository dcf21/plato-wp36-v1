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
from .lightcurve_resample import LightcurveResampler
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

        # Name of the job we are currently working on
        self.job_name = "untitled"

        # Parameters associated with the job we are currently working on
        self.job_parameters = {}

    def read_lightcurve(self, source):
        """
        Read an input lightcurve.

        :param source:
            A dictionary specifying the source of the lightcurve. It should contain the fields
            <source>, <filename> and <directory>.
        :type source:
            dict
        """

        # Extract fields from input data structure
        lc_source = source.get('source', 'memory')
        assert lc_source in ('memory', 'archive', 'lcsg')
        lc_filename = source.get('filename', 'lightcurve.dat')
        lc_directory = source.get('directory', 'test_lightcurves')

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Read input lightcurve
        if lc_source == 'memory':
            lc = self.lightcurves_in_memory[lc_directory][lc_filename]
        else:
            if lc_source == 'lcsg':
                lc_reader = read_lcsg_lightcurve
            elif lc_source == 'archive':
                lc_reader = LightcurveArbitraryRaster.from_file
            else:
                raise ValueError("Unknown lightcurve source <{}>".format(lc_source))

            # Load lightcurve
            with TaskTimer(job_name=self.job_name, target_name=lc_filename, task_name='load_lc',
                           parameters=self.job_parameters, time_logger=time_log):
                lc = lc_reader(
                    filename=lc_filename,
                    directory=lc_directory
                )

        # Close connection to message queue
        time_log.close()

        # Return lightcurve object
        return lc

    def write_lightcurve(self, lightcurve, target):
        """
        Write an output lightcurve.

        :param lightcurve:
            The Lightcurve object to write out.
        :type lightcurve:
            LightcurveArbitraryRaster
        :param target:
            A dictionary specifying the destination for the lightcurve. It should contain the fields
            <source>, <filename> and <directory>.
        :type target:
            dict
        """

        # Extract fields from input data structure
        lc_target = target.get('source', 'memory')
        assert lc_target in ('memory', 'archive', 'lcsg')
        lc_filename = target.get('filename', 'lightcurve.dat')
        lc_directory = target.get('directory', 'test_lightcurves')

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Write output
        if lc_target == "archive":
            with TaskTimer(job_name=self.job_name, target_name=lc_filename, task_name='write_lc',
                           parameters=self.job_parameters, time_logger=time_log):
                lightcurve.to_file(directory=lc_directory, filename=lc_filename)
                self.lightcurves_written.append({
                    'source': 'archive',
                    'filename': lc_filename,
                    'directory': lc_directory
                })
        else:
            if lc_directory not in self.lightcurves_in_memory:
                self.lightcurves_in_memory[lc_directory] = {}
            self.lightcurves_in_memory[lc_directory][lc_filename] = lightcurve

        # Close connection to message queue
        time_log.close()

    def delete_lightcurve(self, lc_source):
        """
        Delete a lightcurve.

        :param lc_source:
            A dictionary specifying the source for the input lightcurve. It should contain the fields
            <source>, <filename> and <directory>.
        :type lc_source:
            dict
        """

        # Extract fields from input data structure
        source = lc_source.get('source', 'memory')
        assert source in ('memory', 'archive', 'lcsg')
        filename = lc_source.get('filename', 'lightcurve.dat')
        directory = lc_source.get('directory', 'test_lightcurves')

        # Delete lightcurve
        if lc_source == 'memory':
            del self.lightcurves_in_memory[lc_directory][lc_filename]
        elif lc_source == 'archive':
            # Full path for this lightcurve
            file_path = os.path.join(settings['lcPath'], directory, filename)

            if os.path.exists(file_path):
                os.unlink(file_path)

    def delete_all_products(self):
        """
        Delete all of the lightcurves we have generated.
        """

        for item in self.lightcurves_written:
            self.delete_lightcurve(lc_source=item)

    def psls_synthesise(self, job_name, target, specs):
        """
        Perform the task of synthesising a lightcurve using PSLS.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param target:
            A dictionary specifying the destination for the lightcurve. It should contain the fields
            <source>, <filename> and <directory>.
        :type target:
            dict
        :param specs:
            Specifications for the lightcurve we are to synthesise. The dictionary should define the following keys:
            <duration>, <enable_transits>, <planet_radius>, <orbital_period>, <semi_major_axis>, <orbital_angle>
        :type specs:
            dict
        """
        logging.info("Running PSLS synthesis")
        self.job_name = job_name
        out_id = os.path.join(
            target.get('directory', 'test_lightcurves'),
            target.get('filename', 'lightcurve.dat')
        )

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Do synthesis
        with TaskTimer(job_name=job_name, target_name=out_id, task_name='psls_synthesis',
                       parameters=self.job_parameters, time_logger=time_log):
            synthesiser = PslsWrapper()
            synthesiser.configure(**specs)
            lc_object = synthesiser.synthesise()
            synthesiser.close()

        # Write output
        self.write_lightcurve(lightcurve=lc_object, target=target)

        # Close connection to message queue
        time_log.close()

    def batman_synthesise(self, job_name, target, specs):
        """
        Perform the task of synthesising a lightcurve using batman.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param target:
            A dictionary specifying the destination for the lightcurve. It should contain the fields
            <source>, <filename> and <directory>.
        :type target:
            dict
        :param specs:
            Specifications for the lightcurve we are to synthesise. The dictionary should define the following keys:
            <duration>, <enable_transits>, <planet_radius>, <orbital_period>, <semi_major_axis>, <orbital_angle>
        :type specs:
            dict
        """
        logging.info("Running Batman synthesis")
        self.job_name = job_name
        out_id = os.path.join(
            target.get('directory', 'test_lightcurves'),
            target.get('filename', 'lightcurve.dat')
        )

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Do synthesis
        with TaskTimer(job_name=job_name, target_name=out_id, task_name='batman_synthesis',
                       parameters=self.job_parameters, time_logger=time_log):
            synthesiser = BatmanWrapper()
            synthesiser.configure(**specs)
            lc_object = synthesiser.synthesise()
            synthesiser.close()

        # Write output
        self.write_lightcurve(lightcurve=lc_object, target=target)

        # Close connection to message queue
        time_log.close()

    def lightcurves_multiply(self, job_name, input_1, input_2, output):
        """
        Perform the task of multiplying two lightcurves together.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param input_1:
            A dictionary specifying the source for the first lightcurve. It should contain the fields
            <source>, <filename> and <directory>.
        :type input_1:
            dict
        :param input_2:
            A dictionary specifying the source for the second lightcurve. It should contain the fields
            <source>, <filename> and <directory>.
        :type input_2:
            dict
        :param output:
            A dictionary specifying the destination for the lightcurve. It should contain the fields
            <source>, <filename> and <directory>.
        :type output:
            dict
        """
        logging.info("Multiplying lightcurves")
        self.job_name = job_name
        out_id = os.path.join(
            output.get('directory', 'test_lightcurves'),
            output.get('filename', 'lightcurve.dat')
        )

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Load lightcurve 1
        lc_1 = self.read_lightcurve(source=input_1)

        # Load lightcurve 2
        lc_2 = self.read_lightcurve(source=input_2)

        # Multiply lightcurves together
        with TaskTimer(job_name=job_name, target_name=out_id, task_name='multiplication',
                           parameters=self.job_parameters, time_logger=time_log):
            result = lc_1 * lc_2

        # Store result
        self.write_lightcurve(lightcurve=result, target=output)

        # Close connection to message queue
        time_log.close()

    def verify_lightcurve(self, job_name, source):
        """
        Perform the task of verifying a lightcurve.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param source:
            A dictionary specifying the source for the input lightcurve. It should contain the fields
            <source>, <filename> and <directory>.
        :type source:
            dict
        """
        self.job_name = job_name
        input_id = os.path.join(
            source.get('directory', 'test_lightcurves'),
            source.get('filename', 'lightcurve.dat')
        )

        logging.info("Verifying <{input_id}>.".format(input_id=input_id))

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Read input lightcurve
        lc = self.read_lightcurve(source=source)

        # Verify lightcurve
        with TaskTimer(job_name=job_name, target_name=input_id, task_name='verify',
                           parameters=self.job_parameters, time_logger=time_log):
            logging.info("Lightcurve <{}> time span {:.1f} to {:.1f}".format(input_id,
                                                                             np.min(lc.times),
                                                                             np.max(lc.times)))

            logging.info("Lightcurve <{}> flux range {:.6f} to {:.6f}".format(input_id,
                                                                              np.min(lc.fluxes),
                                                                              np.max(lc.fluxes)))

            # Run first code for checking LCs
            error_count = lc.check_fixed_step(verbose=True, max_errors=4)

            if error_count == 0:
                logging.info("V1: Lightcurve <{}> has fixed step".format(input_id))
            else:
                logging.info(
                    "V1: Lightcurve <{}> doesn't have fixed step ({:d} errors)".format(input_id, error_count))

            # Run second code for checking LCs
            error_count = lc.check_fixed_step_v2(verbose=True, max_errors=4)

            if error_count == 0:
                logging.info("V2: Lightcurve <{}> has fixed step".format(input_id))
            else:
                logging.info(
                    "V2: Lightcurve <{}> doesn't have fixed step ({:d} errors)".format(input_id, error_count))

        # Close connection to message queue
        time_log.close()

    def rebin_lightcurve(self, job_name, cadence, source, target):
        """
        Perform the task of re-binning a lightcurve.

        :param job_name:
            Specify the name of the job that these tasks is part of.
        :type job_name:
            str
        :param cadence:
            New time cadence for lightcurve, seconds.
        :type cadence:
            float
        :param source:
            A dictionary specifying the source for the input lightcurve. It should contain the fields
            <source>, <filename> and <directory>.
        :type source:
            dict
        :param target:
            A dictionary specifying the target for the output lightcurve. It should contain the fields
            <source>, <filename> and <directory>.
        :type target:
            dict
        """
        self.job_name = job_name
        input_id = os.path.join(
            source.get('directory', 'test_lightcurves'),
            source.get('filename', 'lightcurve.dat')
        )

        logging.info("Rebinning <{input_id}>.".format(input_id=input_id))

        # Open connections to transit results and run times to output message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)

        # Read input lightcurve
        lc = self.read_lightcurve(source=source)

        # Re-bin lightcurve
        with TaskTimer(job_name=job_name, target_name=input_id, task_name='binning',
                           parameters=self.job_parameters, time_logger=time_log):
            start_time = np.min(lc.times)
            end_time = np.max(lc.times)
            new_times = np.arange(start_time, end_time, cadence / 86400)  # Array of times (days)

            resampler = LightcurveResampler(input_lc=lc)
            new_lc = resampler.onto_raster(output_raster=new_times)

            # Eliminate nasty edge effects
            new_lc.fluxes[0] = 1
            new_lc.fluxes[-1] = 1

        # Write output
        self.write_lightcurve(lightcurve=new_lc, target=target)

        # Close connection to message queue
        time_log.close()

    def transit_search(self, job_name, lc_duration, tda_name, source, search_settings):
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
        :param source:
            A dictionary specifying the source for the input lightcurve. It should contain the fields
            <source>, <filename> and <directory>.
        :type source:
            dict
        :param search_settings:
            Dictionary of settings which control how we search for transits.
        :type search_settings:
            dict
        """
        self.job_name = job_name
        input_id = os.path.join(
            source.get('directory', 'test_lightcurves'),
            source.get('filename', 'lightcurve.dat')
        )

        logging.info("Running <{input_id}> through <{tda_name}> with duration {lc_days:.1f}.".format(
            input_id=input_id,
            tda_name=tda_name,
            lc_days=lc_duration)
        )

        # Record start time
        start_time = time.time()

        # Open connections to transit results and run times to RabbitMQ message queues
        time_log = RunTimesToRabbitMQ(results_target=self.results_target)
        result_log = ResultsToRabbitMQ(results_target=self.results_target)

        # Read input lightcurve
        lc = self.read_lightcurve(source=source)

        # Process lightcurve
        with TaskTimer(job_name=job_name, tda_code=tda_name, target_name=input_id, task_name='transit_detection',
                       parameters=self.job_parameters, time_logger=time_log):
            if tda_name == 'bls_reference':
                x = bls_reference.process_lightcurve(lc=lc, lc_duration=lc_duration, search_settings=search_settings)
            elif tda_name == 'bls_kovacs':
                x = bls_kovacs.process_lightcurve(lc=lc, lc_duration=lc_duration, search_settings=search_settings)
            elif tda_name == 'dst_v26':
                x = dst_v26.process_lightcurve(lc=lc, lc_duration=lc_duration, search_settings=search_settings)
            elif tda_name == 'dst_v29':
                x = dst_v29.process_lightcurve(lc=lc, lc_duration=lc_duration, search_settings=search_settings)
            elif tda_name == 'exotrans':
                x = exotrans.process_lightcurve(lc=lc, lc_duration=lc_duration, search_settings=search_settings)
            elif tda_name == 'qats':
                x = qats.process_lightcurve(lc=lc, lc_duration=lc_duration, search_settings=search_settings)
            elif tda_name == 'tls':
                x = tls.process_lightcurve(lc=lc, lc_duration=lc_duration, search_settings=search_settings)
            else:
                assert False, "Unknown transit detection code <{}>".format(tda_name)

            # Extract output
            output, output_extended = x

        # Test whether transit detection was successful
        quality_control(lc=lc, metadata=output)

        # Send result to message queue
        result_log.record_result(job_name=job_name, tda_code=tda_name, target_name=input_id,
                                 task_name='transit_detection',
                                 parameters=self.job_parameters, timestamp=start_time,
                                 result=output, result_extended=output_extended)

        # Close connection to message queue
        time_log.close()
        result_log.close()

    def do_work(self, task_list, job_name="not set", job_parameters={}, clean_up_products=False):
        """
        Perform a list of tasks sent to us via a list of request structures

        :param job_name:
            Optionally, specify the name of the job that these tasks are part of. If the "job_name" field is specified
            in the tasks, this overrides the job name specified here.
        :type job_name:
            str
        :param job_parameters:
            Parameter values associated with this job.
        :type job_parameters:
            dict
        :param task_list:
            A list of dictionaries describing the tasks we are to perform, in sequence. Each task is assumed to depend
            on the previous tasks, and so they are not run in parallel.
        :type task_list:
            List
        :param clean_up_products:
            Boolean flag indicating whether we should delete any data files we write to disk
        :type clean_up_products:
            bool
        """

        # Check that task list is a list
        assert isinstance(task_list, list)

        # Record job's parameter values
        self.job_parameters = job_parameters

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
                    source=job_description['source'],
                    lc_duration=float(job_description.get('lc_duration', 730)),
                    tda_name=job_description.get('tda_name', 'tls'),
                    search_settings=job_description.get('search_settings', {})
                )

            # Synthesise lightcurve with PSLS
            elif job_description['task'] == 'psls_synthesise':
                self.psls_synthesise(
                    job_name=job_description.get('job_name', job_name),
                    target=job_description['target'],
                    specs=job_description.get('specs', {})
                )

            # Synthesise lightcurve with Batman
            elif job_description['task'] == 'batman_synthesise':
                self.batman_synthesise(
                    job_name=job_description.get('job_name', job_name),
                    target=job_description['target'],
                    specs=job_description.get('specs', {})
                )

            # Multiply two lightcurves together
            elif job_description['task'] == 'multiplication':
                self.lightcurves_multiply(
                    job_name=job_description.get('job_name', job_name),
                    input_1=job_description['input_1'],
                    input_2=job_description['input_2'],
                    output=job_description['output'],
                )

            # Verify lightcurve
            elif job_description['task'] == 'verify':
                self.verify_lightcurve(
                    job_name=job_description.get('job_name', job_name),
                    source=job_description['source'],
                )

            # Delete lightcurve
            elif job_description['task'] == 'delete':
                self.delete_lightcurve(
                    job_name=job_description.get('job_name', job_name),
                    source=job_description['source'],
                )

            # Re-bin lightcurve
            elif job_description['task'] == 'binning':
                self.rebin_lightcurve(
                    job_name=job_description.get('job_name', job_name),
                    source=job_description['source'],
                    target=job_description['target'],
                    cadence=job_description.get('cadence', 25)
                )

            # Unknown task
            else:
                raise ValueError("Unknown task <{}>".format(job_description['task']))

        # Clean up products
        if clean_up_products:
            self.delete_all_products()
