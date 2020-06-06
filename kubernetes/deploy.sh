#!/bin/bash

kubectl apply -f mysql-pv.yaml
kubectl apply -f mysql-debug.yaml

kubectl apply -f rabbitmq-service.yaml
kubectl apply -f rabbitmq-controller.yaml

