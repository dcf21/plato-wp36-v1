#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# errors_list.py

"""
Produce the list of all the error messages in the MySQL database
"""

import json
import logging
import os
import sys
from datetime import datetime

import argparse
from plato_wp36 import connect_db, settings


def errors_list(job=None, task=None):
    """
    List error messages stored in the SQL database.

    :param job:
        Filter results by job name.
    :type job:
        str
    :param task:
        Filter results by task.
    :type task:
        str
    """
    output = sys.stdout

    connector = connect_db.DatabaseConnector()
    db, c = connector.connect_db()

    # Fetch list of error messages
    c.execute("""
SELECT
    parameters, timestamp, results, result_filename,
    j.name AS job, tc.name AS tda, s.hostname AS host, t1.name AS target, t2.name AS task
FROM eas_results x
INNER JOIN eas_jobs j ON j.job_id=x.job_id
INNER JOIN eas_tda_codes tc ON tc.code_id=x.code_id
INNER JOIN eas_servers s ON s.server_id=x.server_id
INNER JOIN eas_targets t1 ON t1.target_id=x.target_id
INNER JOIN eas_tasks t2 ON t2.task_id=x.task_id
WHERE t2.name="error_message"
ORDER BY x.timestamp;
""")
    results_list = c.fetchall()

    # Loop over error messages
    for item in results_list:
        # Filter results
        if (job is not None and job != item['job']) or (task is not None and task != item['task']):
            continue

        # Display results
        time_string = datetime.utcfromtimestamp(item['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        output.write("{} | {:36s} | {}\n{}\n\n".format(
            time_string,
            item['host'], item['parameters'],
            json.loads(item['results'])
        ))


if __name__ == "__main__":
    # Read command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', default=None, type=str, dest='job', help='Filter results by job name')
    parser.add_argument('--task', default=None, type=str, dest='task', help='Filter results by job name')
    args = parser.parse_args()

    # Set up logging
    log_file_path = os.path.join(settings.settings['dataPath'], 'plato_wp36.log')
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S',
                        handlers=[
                            logging.FileHandler(log_file_path),
                            logging.StreamHandler()
                        ])
    logger = logging.getLogger(__name__)
    logger.info(__doc__.strip())

    # Dump results
    errors_list(job=args.job, task=args.task)
