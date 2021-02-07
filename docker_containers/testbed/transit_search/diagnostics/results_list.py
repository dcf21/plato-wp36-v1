#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# results_list.py

"""
Produce the list of all the results in the MySQL database
"""

import logging
import os
import sys
from datetime import datetime

import argparse
from plato_wp36 import connect_db, settings


def results_list():
    output = sys.stdout

    connector = connect_db.DatabaseConnector()
    db, c = connector.connect_db()

    # Fetch list of timings
    c.execute("""
SELECT
    lc_length, timestamp, results, result_filename,
    j.name AS job, tc.name AS tda, s.hostname AS host, t1.name AS target, t2.name AS task
FROM eas_results x
INNER JOIN eas_jobs j ON j.job_id=x.job_id
INNER JOIN eas_tda_codes tc ON tc.code_id=x.code_id
INNER JOIN eas_servers s ON s.server_id=x.server_id
INNER JOIN eas_targets t1 ON t1.target_id=x.target_id
INNER JOIN eas_tasks t2 ON t2.task_id=x.task_id
ORDER BY x.timestamp;
""")
    results_list = c.fetchall()

    # Loop over results
    for item in results_list:
        time_string = datetime.utcfromtimestamp(item['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        output.write("{} |{:22s}|{:18s}|{:32s}|{:18s}|{:6.1f}|{}|{}\n".format(
            time_string,
            item['job'], item['task'], item['host'],
            item['target'], item['lc_length'],
            item['results'], item['result_filename']
        ))


if __name__ == "__main__":
    # Read command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
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
    results_list()
