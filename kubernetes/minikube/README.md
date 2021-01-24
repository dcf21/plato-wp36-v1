# Kubernetes deployment scripts

The scripts in this directory are used to deploy the EAS test bench on a single-node minikube Kubernetes cluster.

As a prerequisite to running these scripts, you need to have built the Docker images containing all the transit detection algorithms using the scripts in the `build_docker_containers` directory.

The steps to deploy the test bench are as follows:

1. Install minikube

    If you need to install minikube, this can be done on a Ubuntu machine as follows:
    
    ```
    apt install apt-transport-https ca-certificates curl software-properties-common
    cd
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
    apt update
    apt-cache policy docker-ce
    apt install docker-ce
    systemctl status docker

    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add
    apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
    apt install kubeadm
    
    wget https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    cp minikube-linux-amd64 /usr/local/bin/minikube
    chmod 755 /usr/local/bin/minikube
    minikube version
   ```

1. Start minikube

    ```
    minikube start --cpus=4 --memory='9g' --mount=true
    ```
    
    You may wish to tweak the number of CPU cores and the amount of RAM made available to the Kubernetes cluster.

2. Mount data directories

    The Kubernetes cluster needs access to the directories containing the input lightcurves and where it should write the output from the transit detection codes:
    
    ```
    minikube mount --uid 999 ../../datadir_output/:/mnt/datadir_output/
    minikube mount --uid 999 ../../datadir_input/:/mnt/datadir_input/
    ```

3. Deploy the test bench Docker containers within Kubernetes

    ```
    ./deploy.sh
    ```

4. Watch the pods start up

    ```
    watch kubectl get pods
    ```
    
    This will show a live list of the containers running within Kubernetes. It often takes a minute or two for them to reach the `Running` state.

5. Run tasks within the test bench

    Start a shell terminal within the Docker container running the test bench, and use this to schedule tests to be run:
    
    ```
    ./plato-shell.sh
    cd src/transit_search
    ./master_node/transit_search_request_psls.py
    ./worker_node/transit_search_worker_v2.py
    ```

6. Restart

    To restart the test bench, for example after changing the code:
    
    ```
    ./restart.sh
    ```

7. Stop the test bench

    To close the test bench down:
    
    ```
    ./stop.sh
    ```

8. Stop minikube

    To close minikube down:
    
    ```
    minikube stop
    minikube delete
    ```

9. Clear out results

    To clear out the output results and start again afresh:
    
    ```
    cd ../datadir_output/
    ./wipe.sh
    ```

