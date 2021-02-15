#!/bin/bash

for item in json/*.json
do
  mkfifo stderr
  cat stderr | sed 's/\(.*\)/[01;31m\1[00m/' &
  ./test_json_task_list.py $@ --tasks $item 2>stderr | sed 's/\(.*\)/[01;32m\1[00m/'
  rm stderr
done
