#!../../../../datadir_local/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# timings_to_csv.py

"""
Dump all of the run times from the MySQL database into a CSV file
"""

import json
import logging
import os
import sys

import argparse
from plato_wp36 import connect_db, settings


def timings_to_csv(job=None, task=None):
    """
    List timings stored in the SQL database.

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

    # Fetch list of jobs
    c.execute("SELECT job_id, name FROM eas_jobs ORDER BY name;")
    job_list = c.fetchall()

    if job is not None:
        job_list = [item for item in job_list if item['name'] == job]

    # Fetch list of tasks
    c.execute("SELECT task_id, name FROM eas_tasks ORDER BY name;")
    task_list = c.fetchall()

    if task is not None:
        task_list = [item for item in task_list if item['name'] == task]

    # Fetch list of TDAs
    c.execute("SELECT code_id, name FROM eas_tda_codes ORDER BY name;")
    code_list = c.fetchall()

    # Loop over jobs
    for job in job_list:

        # Loop over tasks
        for task in task_list:

            # Loop over TDA codes
            for code in code_list:
                # Fetch list of all the parameters we need to display
                c.execute("""
SELECT run_time_wall_clock, run_time_cpu, run_time_cpu_inc_children, parameters
FROM eas_run_times WHERE job_id = %s AND task_id = %s AND code_id = %s;
""", (job['job_id'], task['task_id'], code['code_id'])
                          )
                results = list(c.fetchall())

                # Abort if no database entries matched this search
                if len(results) < 1:
                    continue

                # Compile list of all the parameters we need to display
                all_parameter_names = []
                for row in results:
                    for parameter in json.loads(row['parameters']):
                        if parameter not in all_parameter_names:
                            all_parameter_names.append(parameter)

                # Sort parameter names
                all_parameter_names.sort()

                # Sort results by index
                results.sort(
                    key=lambda k: json.loads(k['parameters'])['index']
                )

                # Loop over timing metrics
                for metric in ["run_time_wall_clock", "run_time_cpu", "run_time_cpu_inc_children"]:

                    # Display heading for this job
                    output.write("\n\n{}  --  {} -- {} -- {}\n\n".format(job['name'], task['name'],
                                                                         code['name'], metric))

                    # Display column headings
                    output.write("# ")
                    for item in all_parameter_names:
                        output.write("{:12}  ".format(item))
                    output.write("\n")

                    # Display results
                    for row in results:
                        # Display parameter values
                        for item in all_parameter_names:
                            parameters = json.loads(row['parameters'])
                            value_string = parameters.get(item, "--")
                            try:
                                value_float = float(value_string)
                                output.write("{:12.8f}  ".format(value_float))
                            except ValueError:
                                output.write("{:12}  ".format(str(value_string)))

                        # Display results
                        output.write("{:.1f}\n".format(row[metric]))

                    # New line
                    output.write("\n")


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

    # Dump timings
    timings_to_csv(job=args.job, task=args.task)
