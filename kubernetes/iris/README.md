# Kubernetes deployment scripts

The scripts in this directory are used to deploy the EAS test-bench on the Iris Kubernetes cluster.

As a prerequisite to running these scripts, you need to have built the Docker images containing all the transit-detection algorithms using the scripts in the `build_docker_containers` directory.

The steps to deploy the test-bench are as follows:

3. **Deploy the test-bench Docker containers within Kubernetes**

    ```
    ./deploy.sh
    ```

4. **Watch the pods start up**

    ```
    watch kubectl get pods
    ```

   This will show a live list of the containers running within Kubernetes. It often takes a minute or two for them to
   reach the `Running` state.

5. **Run tasks within the test-bench**

   Start a shell terminal within the Docker container running the test-bench, and use this to schedule tests to be run:

    ```
    ./plato-shell.sh
    cd transit_search/master_node
    ./submit_json_job_to_cluster.py --tasks json_jobs/202102_tda_timing/tls_timing_full_span.json
    ```

6. **Restart**

   To restart the test-bench, for example after changing the code:

    ```
    ./restart.sh
    ```

7. **Stop the test-bench**

   To close the test-bench down:

    ```
    ./stop.sh
    ```


9. **Clear out results**

   To clear out the output results and start again afresh:

    ```
    ./plato-shell.sh
    cd transit_search/master_node
    ./initialisation.sh
    ```

