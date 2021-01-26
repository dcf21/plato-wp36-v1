#!/bin/bash

kubectl apply -f mysql-pvc.yaml
kubectl apply -f mysql-deployment.yaml

kubectl apply -f rabbitmq-service.yaml
kubectl apply -f rabbitmq-controller.yaml

kubectl apply -f output-pvc.yaml
kubectl apply -f input-pvc.yaml
kubectl apply -f log-results-deployment.yaml
kubectl apply -f log-runtimes-deployment.yaml
kubectl apply -f plato-deployment.yaml

