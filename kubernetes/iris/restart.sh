#!/bin/bash

kubectl delete deployment plato --namespace=plato
kubectl apply -f plato-deployment.yaml

