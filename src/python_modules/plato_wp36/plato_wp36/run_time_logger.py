# -*- coding: utf-8 -*-
# run_time_logger.py

import socket
import sqlite3
import os
import re
from .settings import settings


class RunTimeLogger:
    _schema = """
    
    -- Table of TDA codes
    CREATE TABLE eas_tda_codes (
        code_id INTEGER PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL
    );
    
    -- Table of server hostnames
    CREATE TABLE eas_servers (
        server_id INTEGER PRIMARY KEY,
        hostname VARCHAR(255) UNIQUE NOT NULL
    );
    

    -- Table of code run times
    CREATE TABLE eas_run_times (
        run_id INTEGER PRIMARY KEY,
        code_id INTEGER NOT NULL,
        server_id INTEGER NOT NULL,
        lc_length REAL NOT NULL,
        run_time_wall_clock REAL,
        run_time_cpu REAL,
        FOREIGN KEY (code_id) REFERENCES eas_tda_codes (code_id),
        FOREIGN KEY (server_id) REFERENCES eas_servers (server_id)
    );

"""

    def __init__(self, refresh=False, create=True, db_path=os.path.join(settings['dataPath'], 'run_time.db')):
        self.db_path = db_path

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
        Create a database record for a new, empty table of performance data.

        :return:
            None
        """

        if not os.path.exists(self.db_path):
            # SQLite databases work faster if primary keys don't auto increment, so remove keyword from schema
            db = sqlite3.connect(self.db_path)
            c = db.cursor()
            schema = re.sub("AUTO_INCREMENT", "", self._schema)
            c.executescript(schema)
            db.commit()
            db.close()

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

        # Look up the ID for this server
        c.execute("SELECT server_id FROM eas_servers WHERE hostname=%s;", (hostname,))
        tmp = c.fetchall()
        if len(tmp) == 0:
            c.execute("INSERT INTO eas_servers (hostname) VALUES (%s);", (hostname,))
            c.execute("SELECT server_id FROM eas_servers WHERE hostname=%s;", (hostname,))
            tmp = c.fetchall()
        server_id = tmp[0]["server_id"]
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

        # Look up the ID for this TDA code
        c.execute("SELECT code_id FROM eas_tda_codes WHERE name=%s;", (code_name,))
        tmp = c.fetchall()
        if len(tmp) == 0:
            c.execute("INSERT INTO eas_tda_codes (name) VALUES (%s);", (code_name,))
            c.execute("SELECT code_id FROM eas_tda_codes WHERE name=%s;", (code_name,))
            tmp = c.fetchall()
        code_id = tmp[0]["code_id"]
        return code_id

    def create_log_entry(self, tda_code, lc_length, run_time_wall_clock, run_time_cpu):
        # Look up the uid for this server
        server_id = self.get_server_id()

        # Look up the uid for the TDA code
        code_id = self.get_code_id(tda_code)

        # Add row to sqlite3 database
        db = sqlite3.connect(self.db_path)
        c = db.cursor()
        c.execute("""
INSERT INTO eas_run_times (code_id, server_id, lc_length, run_time_wall_clock, run_time_cpu)
VALUES (%s, %s, %s, %s, %s);
        """, (code_id, server_id, lc_length, run_time_wall_clock, run_time_cpu))
        db.commit()
        db.close()
