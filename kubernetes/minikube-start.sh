#!/bin/bash

minikube start --cpus=4 --memory='9g' --mount=true

minikube mount --uid 999 ../datadir_output/:/mnt/datadir/
minikube mount --uid 999 ../datadir_input/lightcurves_v2/:/mnt/lightcurves_v2

