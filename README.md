# IoTFlow - Artifact



![Overview of IoTFlow](iotflow_figure.pdf)

We use VSA to reconstruct endpoints, cryptographic data, and ICC keys for the flow analysis. We use flow analysis to find data leaks, and connect request/response data with endpoints. With the ICC information of the VSA, we support data flows involving ICC.

* [VSA](VSA/) contains the code of the value set analysis. We provided a [Docker container](VSA/docker/) to run it. Add apps to `apps_to_analyze` and hit `docker compose up` to try it out.
* [FlowAnalysis](FlowAnalysis/) contains the code of the data flow analysis. We again provided a [Docker container](FlowAnalysis/docker/apps_to_analyze/) for easier setup. Add apps to [apps_to_analyze](FlowAnalysis/docker/apps_to_analyze/) and hit `docker compose up` to try it out.
* In [config](config/) we provide the configurations we used for the analysis, e.g., the sources and sinks.
* [Datasets](datasets/) contain the app ids and version codes of the apps we used.
* In [scripts](scripts/) we added code, we used to analyze the obtained results further and generate the tables.