# -*- coding: utf-8 -*-
# results_database.py

import socket
import sqlite3
import os
import re
from .settings import settings

"""
Provides a class used for storing results and time measurements in an SQL database.
"""


class ResultsDatabase:
    """
    Provides a class used for storing results and time measurements in an SQL database.

    :attribute _schema:
        The SQL database schema.
    """

    # SQL database schema
    _schema = """
    
# Create generator database
CREATE TABLE inthesky_generators
(
    generatorId SMALLINT PRIMARY KEY AUTO_INCREMENT,
    name        TEXT
);

# Table of TDA codes
CREATE TABLE eas_tda_codes (
    code_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL
);

# Table of server hostnames
CREATE TABLE eas_servers (
    server_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    hostname VARCHAR(255) UNIQUE NOT NULL
);

# Table of lightcurves
CREATE TABLE eas_targets (
    target_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL
);

# Table of tasks
CREATE TABLE eas_tasks (
    task_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL
);

# Table of code run times
CREATE TABLE eas_run_times (
    run_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    code_id INTEGER NOT NULL,
    server_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    lc_length REAL NOT NULL,
    run_time_wall_clock REAL,
    run_time_cpu REAL,
    FOREIGN KEY (code_id) REFERENCES eas_tda_codes (code_id),
    FOREIGN KEY (server_id) REFERENCES eas_servers (server_id),
    FOREIGN KEY (target_id) REFERENCES eas_targets (target_id),
    FOREIGN KEY (task_id) REFERENCES eas_tasks (task_id)
);

"""

    def __init__(self, refresh=False, create=True):
        """
        Open a handle to the SQLite3 database of task run times. Ensure that the SQLite3 database file exists.

        :param refresh:
            If true, delete any existing SQL database and start afresh [danger!].
        :param create:
            If true, create an empty SQL database if one doesn't already exist.
        """

        if refresh:
            if os.path.exists(db_path):
                os.unlink(db_path)
                create=True

        if not os.path.exists(db_path):
            if create:
                self.check_db_exists()
            else:
                raise IOError("Could not open sqlite database <{}>".format(db_path))

    def check_db_exists(self):
        """
        Check whether an SQL database already exists. If not, create a fresh database with empty table of results.

        :return:
            None
        """

        if not os.path.exists(self.db_path):
            # Open connection to new, empty database
            db = sqlite3.connect(self.db_path)
            c = db.cursor()
            c.row_factory = sqlite3.Row

            # SQLite databases work faster if primary keys don't auto increment, so remove keyword from schema
            schema = re.sub("AUTO_INCREMENT", "", self._schema)
            c.executescript(schema)

            # Commit empty database
            db.commit()
            db.close()

    # Fetch the ID number associated with a particular data generator string ID
    def fetch_generator_key(self, gen_key):
        """
        Return the ID number associated with a particular data generator string ID. Used to track which python scripts
        generate which entries in the database.

        :param gen_key:
            String data generator identifier.
        :return:
            Numeric data generator identifier.
        """

        c.execute("SELECT generatorId FROM plato_generators WHERE name=%s;", (gen_key,))
        tmp = c.fetchall()
        if len(tmp) == 0:
            c.execute("INSERT INTO plato_generators VALUES (NULL, %s);", (gen_key,))
            c.execute("SELECT generatorId FROM plato_generators WHERE name=%s;", (gen_key,))
            tmp = c.fetchall()
        gen_id = tmp[0]["generatorId"]
        return gen_id

    def get_server_id(self, hostname=socket.gethostname()):
        """
            Return the ID number associated with a particular server. Used to keep track of which run time measurements
            come from which servers in a cluster.

            :param hostname:
                String hostname for a server.
            :return:
                Numeric data generator identifier.
            """

        # Open connection to sqlite3 database
        db = sqlite3.connect(self.db_path)
        c = db.cursor()
        c.row_factory = sqlite3.Row

        # Look up the ID for this server
        c.execute("SELECT server_id FROM eas_servers WHERE hostname=?;", (hostname,))
        tmp = c.fetchall()

        # If it doesn't exist, create a new ID
        if len(tmp) == 0:
            c.execute("INSERT INTO eas_servers (hostname) VALUES (?);", (hostname,))
            db.commit()
            c.execute("SELECT server_id FROM eas_servers WHERE hostname=?;", (hostname,))
            tmp = c.fetchall()

        # Extract UID from the data returned by the SQL query
        server_id = tmp[0]["server_id"]
        db.close()
        return server_id

    def get_code_id(self, code_name):
        """
            Return the ID number associated with a particular TDA code. Used to keep track of which run time
            measurements refer to which codes.

            :param code_name:
                String name for a TDA implementation.
            :return:
                Numeric data generator identifier.
            """

        # Open connection to sqlite3 database
        db = sqlite3.connect(self.db_path)
        c = db.cursor()
        c.row_factory = sqlite3.Row

        # Look up the ID for this TDA code
        c.execute("SELECT code_id FROM eas_tda_codes WHERE name=?;", (code_name,))
        tmp = c.fetchall()

        # If it doesn't exist, create a new ID
        if len(tmp) == 0:
            c.execute("INSERT INTO eas_tda_codes (name) VALUES (?);", (code_name,))
            db.commit()
            c.execute("SELECT code_id FROM eas_tda_codes WHERE name=?;", (code_name,))
            tmp = c.fetchall()

        # Extract UID from the data returned by the SQL query
        code_id = tmp[0]["code_id"]
        db.close()
        return code_id

    def get_lightcurve_id(self, lightcurve_name):
        """
            Return the ID number associated with a particular lightcurve. Used to keep track of which data
            refers to which lightcurve.

            :param lightcurve_name:
                String name for a lightcurve.
            :return:
                Numeric data generator identifier.
            """

        # Open connection to sqlite3 database
        db = sqlite3.connect(self.db_path)
        c = db.cursor()
        c.row_factory = sqlite3.Row

        # Look up the ID for this lightcurve
        c.execute("SELECT target_id FROM eas_targets WHERE name=?;", (lightcurve_name,))
        tmp = c.fetchall()

        # If it doesn't exist, create a new ID
        if len(tmp) == 0:
            c.execute("INSERT INTO eas_targets (name) VALUES (?);", (lightcurve_name,))
            db.commit()
            c.execute("SELECT target_id FROM eas_targets WHERE name=?;", (lightcurve_name,))
            tmp = c.fetchall()

        # Extract UID from the data returned by the SQL query
        target_id = tmp[0]["target_id"]
        db.close()
        return target_id

    def get_task_id(self, task_name):
        """
            Return the ID number associated with a particular task in the processing chain.

            :param task_name:
                String name for a task.
            :return:
                Numeric data generator identifier.
            """

        # Open connection to sqlite3 database
        db = sqlite3.connect(self.db_path)
        c = db.cursor()
        c.row_factory = sqlite3.Row

        # Look up the ID for this task in the processing chain
        c.execute("SELECT task_id FROM eas_tasks WHERE name=?;", (task_name,))
        tmp = c.fetchall()

        # If it doesn't exist, create a new ID
        if len(tmp) == 0:
            c.execute("INSERT INTO eas_tasks (name) VALUES (?);", (task_name,))
            db.commit()
            c.execute("SELECT task_id FROM eas_tasks WHERE name=?;", (task_name,))
            tmp = c.fetchall()

        # Extract UID from the data returned by the SQL query
        code_id = tmp[0]["task_id"]
        db.close()
        return code_id

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
