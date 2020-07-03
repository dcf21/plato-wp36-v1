#!../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# results_to_csv.py

"""
Dump all of the run times from the MySQL database into a CSV file
"""

import os
import sys
import argparse
import logging

from plato_wp36 import connect_db, settings

def results_to_csv():
    output = sys.stdout

    connector = connect_db.DatabaseConnector()
    db, c = connector.connect_db()

    # Fetch list of tasks
    c.execute("SELECT task_id, name FROM eas_tasks ORDER BY name;")
    task_list = c.fetchall();

    # Fetch list of TDAs
    c.execute("SELECT code_id, name FROM eas_tda_codes ORDER BY name;")
    code_list = c.fetchall();

    # Fetch list of LC durations
    c.execute("SELECT DISTINCT lc_length FROM eas_run_times ORDER BY lc_length;")
    lc_lengths = c.fetchall();

    # Loop over tasks
    for task in task_list:

        # Loop over timing metrics
        for metric in ["run_time_wall_clock", "run_time_cpu"]:
            output.write("\n\n{} ({})\n\n".format(task['name'], metric))

            # Print column headings
            output.write(",{}\n".format(",".join([str(item['lc_length']) for item in lc_lengths])))

            # Loop over TDA codes
            for code in code_list:
                # Print rows of table
                output.write(code['name'])

                for lc_length in lc_lengths:
                    # Average timings
                    timings_sum = 0
                    timings_count = 1e-8
                    c.execute("""
SELECT {} AS value FROM eas_run_times
WHERE code_id = %s AND
      task_id = %s AND
      lc_length BETWEEN %s-0.01 AND %s+0.01
;
""".format(metric), (code['code_id'], task['task_id'], lc_length['lc_length'], lc_length['lc_length']))
                    for item in c.fetchall():
                        timings_sum += item['value']
                        timings_count += 1
                    output.write(",{:.1f}".format(timings_sum/timings_count))

                # New line
                output.write("\n")


if __name__ == "__main__":
    # Read commandline arguments
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

