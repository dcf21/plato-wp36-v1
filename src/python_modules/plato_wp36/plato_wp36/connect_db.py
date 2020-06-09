# -*- coding: utf-8 -*-
# connect_db.py

"""
Module for connecting to MySQL database for storage of results.
"""

# Ignore SQL warnings
import warnings

import MySQLdb

from .settings import installation_info

warnings.filterwarnings("ignore", ".*Unknown table .*")


class DatabaseConnector:
    """
    Class for connecting to MySQL database
    """

    def __init__(self):
        # Look up MySQL database log in details
        self.db_host = installation_info['db_host']
        self.db_user = installation_info['db_user']
        self.db_password = installation_info['db_password']
        self.db_database = installation_info['db_database']

    def test_database_exists(self):
        """
        Test whether the results database has already been set up.

        :return:
            Boolean indicating whether the database has been set up
        """

        try:
            db = MySQLdb.connect(host=self.db_host, user=self.db_user, passwd=self.db_password, db=self.db_database)
        except MySQLdb._exceptions.OperationalError as exception:
            if "Unknown database" not in str(exception):
                raise
            return False

        db.close()
        return True

    def connect_db(self, database=0):
        """
        Return a new MySQLdb connection to the database.

        :param database:
            The name of the database we should connect to
        :return:
            List of [database handle, connection handle]
        """

        if database == 0:
            database = self.db_database

        db = MySQLdb.connect(host=self.db_host, user=self.db_user, passwd=self.db_password, db=database)
        c = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        db.set_character_set('utf8mb4')
        c.execute('SET NAMES utf8mb4;')
        c.execute('SET CHARACTER SET utf8mb4;')
        c.execute('SET character_set_connection=utf8mb4;')

        return db, c
