#!/bin/bash

# Make sure we're running in the right directory
cd "$(dirname "$0")"
cwd=`pwd`

virtualenv -p python3 virtualenv
virtualenv/bin/pip install -r requirements.txt
