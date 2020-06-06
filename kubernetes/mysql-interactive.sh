#!/bin/bash

kubectl run -it --rm --image=mysql:8.0 --restart=Never mysql-client -- mysql -h mysql -pplato

