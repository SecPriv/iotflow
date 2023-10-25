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
