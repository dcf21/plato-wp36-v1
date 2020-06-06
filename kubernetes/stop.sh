#!/bin/bash

kubectl delete deployment,svc mysql
kubectl delete pvc mysql-pv-claim
kubectl delete pv mysql-pv-volume

kubectl delete svc rabbitmq-service
kubectl delete rc rabbitmq-controller

