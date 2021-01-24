#!/bin/bash

mkdir -p ../../datadir_output/mysql
chmod 775 ../../datadir_output/mysql

mkdir -p ../../datadir_output/json_out
chmod 775 ../../datadir_output/json_out

mkdir -p ../../datadir_output/scratch
chmod 775 ../../datadir_output/scratch

kubectl apply -f mysql-pv.yaml
kubectl apply -f mysql-deployment.yaml

kubectl apply -f rabbitmq-service.yaml
kubectl apply -f rabbitmq-controller.yaml

kubectl apply -f datadir-pv.yaml
kubectl apply -f lightcurves-pv.yaml
kubectl apply -f log-results-deployment.yaml
kubectl apply -f log-runtimes-deployment.yaml
kubectl apply -f plato-deployment.yaml

