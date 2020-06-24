#!/bin/bash

minikube start --cpus=4 --memory='9g' --mount=true

minikube mount --uid 999 ../../datadir/:/mnt/datadir/
minikube mount --uid 999 ../../lightcurves_v2/:/mnt/lightcurves_v2

