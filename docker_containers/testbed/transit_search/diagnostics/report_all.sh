#!/bin/bash

# Make sure we run this in the right directory
cd "$(dirname "$0")"
cwd=`pwd`

# Redirect output to file
exec &> results.log

# Record results
./timings_list.py
./results_list.py
./timings_to_csv.py
./results_to_csv.py
./pass_fail_to_csv.py

