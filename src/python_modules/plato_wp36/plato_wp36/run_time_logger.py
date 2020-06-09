# -*- coding: utf-8 -*-
# run_time_logger.py

import os
from .settings import settings

"""
Provides a class used for compiling a database of the run times of various tasks.
"""


class RunTimeLogger:
    """
    Provides a class used for compiling a database of the run times of various tasks.
    """

    def __init__(self, refresh=False, create=True, db_path=os.path.join(settings['dataPath'], 'run_time.db')):
        """
        Open a handle to the SQLite3 database of task run times. Ensure that the SQLite3 database file exists.

        :param refresh:
            If true, delete any existing SQLite3 database and start afresh [danger!].
        :param create:
            If true, create an empty SQLite3 database if one doesn't already exist.
        :param db_path:
            The path to the SQLite3 database file. By default, we store it in the <datadir> directory at the root of
            the installation.
        """
        self.db_path = db_path

        if refresh:
            if os.path.exists(db_path):
                os.unlink(db_path)
                create = True

        if not os.path.exists(db_path):
            if create:
                self.check_db_exists()
            else:
                raise IOError("Could not open sqlite database <{}>".format(db_path))

    def create_log_entry(self, tda_code, target_name, task_name, lc_length, run_time_wall_clock, run_time_cpu):
        """
        Create a new entry in the database for a new code performance measurement.

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
        :param run_time_wall_clock:
            The run time of the step in wall clock time (seconds)
        :type run_time_wall_clock:
            float
        :param run_time_cpu:
            The run time of the step in CPU seconds
        :type run_time_cpu:
            float
        :return:
            None
        """

        # Look up the uid for this server
        server_id = self.get_server_id()

        # Look up the uid for the TDA code
        code_id = self.get_code_id(code_name=tda_code)

        # Look up the uid for this lightcurve
        target_id = self.get_lightcurve_id(lightcurve_name=target_name)

        # Look up the uid for this task in the processing chain
        task_id = self.get_task_id(task_name=task_name)

        # Add row to sqlite3 database
        db = sqlite3.connect(self.db_path)
        c = db.cursor()
        c.row_factory = sqlite3.Row

        c.execute("""
INSERT INTO eas_run_times (code_id, server_id, target_id, task_id, lc_length, run_time_wall_clock, run_time_cpu)
VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (code_id, server_id, target_id, task_id, lc_length, run_time_wall_clock, run_time_cpu))
        db.commit()
        db.close()
