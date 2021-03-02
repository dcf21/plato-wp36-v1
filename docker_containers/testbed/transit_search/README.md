# Algorithm speed test

The scripts in this directory provide a command-line interface for launching timed tests of how long transit-detection codes take to run. They should be run inside a Docker container where the codes have been installed.

To insert a test into a job queue, run the script:

```
./master_node/transit_search_request.py
```

To start running tests from the job queue on a node in a processing cluster, run:

```
./worker_node/transit_search_worker.py
```

To display the results in CSV format:

```
./diagnostics/results_to_csv.py
```

Other scripts are as follows:

* `diagnostics/display_message_queue.py` -- Display a list of tests which are currently waiting in the queue.

* `diagnostics/verify_lcs.py` -- Open the input light curves, and check their time span and sampling interval.
