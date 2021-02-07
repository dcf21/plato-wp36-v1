#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# results_to_csv.py

"""
Dump all of the results of transit-detection runs from the MySQL database into a CSV file
"""

import logging
import os
import sys

import argparse
from plato_wp36 import connect_db, settings


def results_to_csv():
    output = sys.stdout

    connector = connect_db.DatabaseConnector()
    db, c = connector.connect_db()

    # Fetch list of jobs
    c.execute("SELECT job_id, name FROM eas_jobs ORDER BY name;")
    job_list = c.fetchall()

    # Fetch list of tasks
    c.execute("SELECT task_id, name FROM eas_tasks ORDER BY name;")
    task_list = c.fetchall()

    # Fetch list of TDAs
    c.execute("SELECT code_id, name FROM eas_tda_codes ORDER BY name;")
    code_list = c.fetchall()

    # Fetch list of LC durations
    c.execute("SELECT DISTINCT lc_length FROM eas_results ORDER BY lc_length;")
    lc_lengths = c.fetchall()

    # Loop over jobs
    for job in job_list:

        # Loop over tasks
        for task in task_list:

            # Loop over TDA codes
            for code in code_list:
                # Check whether we have any results to report
                c.execute("SELECT COUNT(*) FROM eas_results WHERE job_id = %s AND task_id = %s AND code_id = %s;",
                          (job['job_id'], task['task_id'], code['code_id'])
                          )
                if c.fetchone()['COUNT(*)'] < 1:
                    continue

                # Loop over lightcurve lengths
                for lc_length in lc_lengths:
                    output.write("\n\n{}  --  {} -- {} -- {}\n\n".format(job['name'], task['name'],
                                                                         code['name'], lc_length['lc_length']))
                    # Fetch all results from this configuration
                    c.execute("""
SELECT results FROM eas_results
WHERE job_id = %s AND
      code_id = %s AND
      task_id = %s AND
      lc_length BETWEEN %s-0.01 AND %s+0.01
;
""", (job['job_id'], code['code_id'], task['task_id'], lc_length['lc_length'], lc_length['lc_length']))
                    for item in c.fetchall():
                        output.write("{}\n".format(item['results']))

                # New line
                output.write("\n")


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
    results_to_csv()
