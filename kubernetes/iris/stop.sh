#!/bin/bash

kubectl delete deployment plato --namespace=plato
kubectl delete deployment log-results --namespace=plato
kubectl delete deployment log-runtimes --namespace=plato
kubectl delete pvc output-pvc --namespace=plato
kubectl delete pvc input-pvc --namespace=plato

kubectl delete deployment,svc mysql --namespace=plato
kubectl delete pvc mysql-pvc --namespace=plato

kubectl delete svc rabbitmq-service --namespace=plato
kubectl delete rc rabbitmq-controller --namespace=plato

