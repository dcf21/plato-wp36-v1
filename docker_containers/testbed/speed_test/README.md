# Algorithm speed test

The scripts in this directory provide a command-line interface for launching timed tests of how long transit detection codes take to run. They should be run inside a Docker container where the codes have been installed.

To insert a test into a job queue, run the script:

```
./speed_test_request.py
```

To start running tests from the job queue on a node in a processing cluster, run:

```
./speed_test_worker.py
```

To display the results in CSV format:

```
./results_to_csv.py
```

Other scripts are as follows:

* `display_message_queue.py` -- Display a list of tests which are currently waiting in the queue.

* `verify_lcss.py` -- Open the input light curves, and check their time span and sampling interval.
