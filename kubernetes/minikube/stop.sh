#!/bin/bash

kubectl delete deployment plato
kubectl delete deployment log-results
kubectl delete deployment log-runtimes
kubectl delete pvc datadir-pv-claim
kubectl delete pv datadir-pv-volume
kubectl delete pvc lightcurves-pv-claim
kubectl delete pv lightcurves-pv-volume

kubectl delete deployment,svc mysql
kubectl delete pvc mysql-pv-claim
kubectl delete pv mysql-pv-volume

kubectl delete svc rabbitmq-service
kubectl delete rc rabbitmq-controller
