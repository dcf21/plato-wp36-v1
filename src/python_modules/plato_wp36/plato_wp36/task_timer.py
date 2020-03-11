# -*- coding: utf-8 -*-
# task_timer.py

import time

import os
from .settings import settings
from .run_time_logger import RunTimeLogger

class TaskTimer:
    def __init__(self, code_name, lc_length, time_logger=RunTimeLogger()):

        assert isinstance(time_logger, RunTimeLogger)
        self.time_logger = time_logger

    def measure_time(self):
        raise NotImplementedError

    def __enter__(self):
        self.start_time = self.measure_time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = self.measure_time()