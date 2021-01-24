#!/bin/bash

kubectl delete deployment plato
kubectl apply -f plato-deployment.yaml
