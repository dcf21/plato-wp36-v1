#!/bin/bash

minikube start --mount=true
minikube mount --uid 999 --mount-string=../datadir/:/mnt/datadir/

