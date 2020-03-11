#!../../virtualenv/bin/python3
# -*- coding: utf-8 -*-
# initialisation.py

from plato_wp36.run_time_logger import RunTimeLogger

# Make sure that sqlite3 database exists to hold code run time data
RunTimeLogger(refresh=True)
