#!/bin/bash

minikube start --cpus=2 --memory='4g' --mount=true

minikube mount --uid 999 ../../datadir_output/:/mnt/datadir/
minikube mount --uid 999 ../../datadir_input/:/mnt/datadir_input/

