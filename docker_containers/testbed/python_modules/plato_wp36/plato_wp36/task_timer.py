# -*- coding: utf-8 -*-
# task_timer.py

"""
A class which can be used to wrap segments of code, and time how long they take to run, in both wall-clock time and also
CPU time. To use, wrap your code as follows:

with TaskTimer( <settings> ):
    <code_segment>

"""

import resource
import time

from .run_time_logger import RunTimesToRabbitMQ


class TaskTimer:
    """
    A class which can be used to wrap segments of code, and time how long they take to run, in both wall-clock time
    and also CPU time.
    """

    def __init__(self, job_name, tda_code="", target_name="", task_name="null", parameters={},
                 time_logger=RunTimesToRabbitMQ()):
        """
        Create a new timer.

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
        :param time_logger:
            The handle to the message queue where this time measurement is to be recorded.
        """

        # Ensure that time_logger is a genuine <RunTimesToRabbitMQ> object
        assert isinstance(time_logger, RunTimesToRabbitMQ)

        # Store the state of this timer
        self.job_name = job_name
        self.tda_code = tda_code
        self.target_name = target_name
        self.task_name = task_name
        self.parameters = parameters
        self.time_logger = time_logger

    @staticmethod
    def measure_time():
        """
        Implementation of the function(s) we use to measure how long this process has been running.

        :return:
            A dictionary of time measurements
        """
        return {
            # Wall clock time
            'wall_clock': time.time(),

            # CPU core seconds
            'cpu': time.process_time(),

            # CPU core seconds as reported by <resource> package, including child processes
            'cpu_inc_children': resource.getrusage(resource.RUSAGE_SELF).ru_utime +
                            resource.getrusage(resource.RUSAGE_SELF).ru_stime +
                            resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime +
                            resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime
        }

    def __enter__(self):
        """
        Start timing a task
        """

        # Record the start time of the task
        self.start_time = self.measure_time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Stop timing the task

        :param exc_type:
            Exception type
        :param exc_val:
            Exception value
        :param exc_tb:
            Exception traceback
        :return:
        """

        # Record the end time of the task
        self.end_time = self.measure_time()

        # Calculate run time
        run_times = {}
        for key in self.end_time:
            run_times[key] = self.end_time[key] - self.start_time[key]

        # Record run time
        self.time_logger.record_timing(
            job_name=self.job_name,
            tda_code=self.tda_code,
            target_name=self.target_name,
            task_name=self.task_name,
            parameters=self.parameters,
            timestamp=self.start_time['wall_clock'],
            run_time_wall_clock=run_times['wall_clock'],
            run_time_cpu=run_times['cpu'],
            run_time_cpu_inc_children=run_times['cpu_inc_children']
        )
