# IoTFlow - Artifact



![Overview of IoTFlow](iotflow_figure.pdf)

We use VSA to reconstruct endpoints, cryptographic data, and ICC keys for the flow analysis. We use flow analysis to find data leaks, and connect request/response data with endpoints. With the ICC information of the VSA, we support data flows involving ICC.

* [VSA](VSA/) contains the code of the value set analysis.
* [FlowAnalysis](FlowAnalysis/) contains the code of the data flow analysis.
* In [config](config/) we provide the configurations we used for the analysis, e.g., the sources and sinks.
* [Datasets](datasets/) contain the app ids and version codes of the apps we used.
* In [scripts](scripts/) we added code, we used to analyze the obtained results further and generate the tables.