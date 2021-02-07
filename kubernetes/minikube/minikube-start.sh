#!/bin/bash

minikube start --cpus=12 --memory='9g' --mount=true

minikube mount --uid 999 ../../datadir_output/:/mnt/datadir_output/
minikube mount --uid 999 ../../datadir_input/:/mnt/datadir_input/

