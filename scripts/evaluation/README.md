# Evaluation

Evaluation scripts we used to create Tables and analyze results of IoTFlow.
To run the Jupyter Notebooks and scripts make sure to adjust the paths to load your result files.

* [Performance](general_stats/) evaluation, we used for Section 4.2 and Table 1
* How do companion apps and devices communicate?
    * [Direct device communication](direct_device_communication/) scripts we used to extract information for Section 4.4.1, and Table 2.
    * [URL protocols schemes](url_protocol_schemes/) evaluation used for Section 4.4.2 and Table 3
    * [Certificate pinning](certificate_pinning/) scripts to evaluate pinning data, we used it for Section 4.4.3, and Table 4
* Who are companion apps communicating with?
    * [Advertisement and trackers](advertisement_and_trackers/) classification scripts, we used for Section 4.4.1, and Table 5
    * [Geographic location](geographic_location/) of domains (Section 4.4.2, and Table 6)
    * [Scripts to find abandoned domains](abandoned_domains/), we used for Section 4.4.3
* Which data are companion apps sharing (and how)?,
    * [Permissions](permissions/) analysis of Section 4.5.1.
    * [Data flow](data_flows/) study used to create data for Section 4.5.2, and Table 7
    * [Encryption analysis](encryption_analysis/) of Section 4.5.3 and Table 8
* [Dynamic analysis](dynamic_analysis/) used in Section 5, and the comparison to IoTFlow.


## Loading datasets

We wrote several helper functions to load the analysis results and process them. We provide here an example folder structure and the function arguments to load their data:


/server_data/
  - results/
    - vsa/
      - neupane/
        - amqp/*.json
        - ...
      - gp_2022/
        - amqp/*.json
        - ...
      - ...
    - pinning/
        - nsc_results*.csv
        - string_results*.csv
        - ...
    - permissions/
        - neupane/*.json
        - ...
    - iotflow/
        - neupane/
            - ...
        - gp_2022/
            - ...
        - ...
    - mapping.json


### VSA

#### Companion apps - verified dataset
```
companion_app_dataset = util.get_verified_dataset("/server_data/results/", "", "/server_data/results/mapping.json")
```
1. `"/server_data/results/"` the base path of the result folder that contains the following folders `neupane`, `iotflow`, and `iotspotter`.
2. `""` subfolder in every dataset (`neupane`, `iotflow`, and `iotspotter`) that contains the results. In our case, it is blank, as the results are directly in the dataset folders. However, if you run the analysis multiple times, you might have a subfolder like `"/2023_04_06/"` indicating the experiment's start date in each dataset folder.
3. `"/server_data/results/mapping.json"`, the file tells the Python script which results to consider for apps that are in multiple companion app datasets.



#### GP_2022 dataset
```
gp_2022_Dataset = util.loadAllData("/server_data/results/gp_2022/", True)
```

1. `"/server_data/results/gp_2022/"` the base path of the results to load. It is expected that this folder contains the subfolder of different executions, e.g., `mqtt`, `coap`, `endpoints`.
2. The optional second argument set to `True` tells the script to exclude results from specific apps. Apps that are in the general purpose dataset, but (1) are also in one of the companion app datasets, and (2) we manually labeled as companion apps.


#### Results from own execution
```
util.loadAllData("/VSA/docker/results/")
```

1. `"VSA/docker/results/"` The path to the results of your own analysis execution



### Certificate pinning

```
gp_2022 = load_nsc_csv("/server_data/results/pinning/nsc_results_gp_2022.csv", {})

neupane = load_nsc_csv("/server_data/results/pinning/nsc_results_neupane.csv", {})
iotspotter = load_nsc_csv("/server_data/results/pinning/nsc_results_iotspotter.csv", {})
iotprofiler = load_nsc_csv("/server_data/results/pinning/nsc_results_iotprofiler.csv", {})

gp_2022 = load_string_csv("/server_data/results/pinning/string_results_gp_2022.csv",gp_2022)

neupane = load_string_csv("/server_data/results/pinning/string_results_neupane.csv", neupane)
iotspotter = load_string_csv("/server_data/results/pinning/string_results_iotspotter.csv", iotspotter)
iotprofiler = load_string_csv("/server_data/results/pinning/string_results_iotprofiler.csv", iotprofiler)

```


1. `"pinning/*.csv"` path to the summarized results file, created with https://github.com/NEU-SNS/app-tls-pinning/blob/main/code/certificate-pinning/StaticAnalysis/networkSecurityConfig/compile_nsc_results.py and https://github.com/NEU-SNS/app-tls-pinning/blob/main/code/certificate-pinning/StaticAnalysis/stringSearch/compile_string_search_results.py .
2. argument: result dictionary, either start with an empty one `{}`, or if results should be aggregated (nsc + string) for the same dataset, add the previous loaded.

### Permissions

```
neupane = load_app_data("/server_data/results/permissions/neupane/", "neupane")
iotprofiler = load_app_data("/server_data/results/permissions/iotprofiler/", "iotprofiler")
iotspotter = load_app_data("/server_data/results/permissions/iotspotter/", "iotspotter")

gp_2022 = load_app_data("/server_data/results/permissions/gp_2022/", "gp_2022")
```
1. path to permission results
2. dataset name, to specify which dataset it currently loads, which is relevant to exclude duplicated apps from the companion app dataset and companion apps from the general_purpose app dataset.

### DFA

```
path_bl_run_config = "FlowAnalysis/docker/config/bl_config.xml"

mapping_file = "/server_data/results/mapping.json"

general_local: List[FlowDroidRun] = parse_local_dataset("/server_data/results/iotflow/gp_2022")
general_bl: List[FlowDroidRun] = parse_bl_dataset("/server_data/results/iotflow/gp_2022")
general_general: List[FlowDroidRun] = parse_general_dataset("/server_data/results/iotflow/gp_2022")


verfied_local: List[FlowDroidRun] = parse_verified_dataset_local("/server_data/results/iotflow/", mapping_file)
verfied_bl: List[FlowDroidRun] = parse_verified_dataset_bl("/server_data/results/iotflow/", mapping_file)
verfied_general: List[FlowDroidRun] = parse_verified_dataset_general("/server_data/results/iotflow/",
                                                                     mapping_file)
```
* `bl_config.xml` path to the bl_config. The script uses it to extract icc sinks. The configuration can be found in `FlowAnalysis/docker/config/bl_config.xml`.
* Mapping file for companion app dataset
* `parse_dataset` 1. argument path to iotflow results
* `parse_verified_dataset` 1. argument path to iotflow results,  2. argument mapping file path


### Other

* `mapping.json` is a file that tells the Python script which results to consider for apps that are in multiple companion app datasets. We put the file used on the server `/rseults/mapping.json`.
