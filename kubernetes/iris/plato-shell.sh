#!/bin/bash

kubectl exec -it `kubectl get pods --field-selector="status.phase=Running" --no-headers -o custom-columns=":metadata.name" | grep plato | head -n 1` -- /bin/bash

