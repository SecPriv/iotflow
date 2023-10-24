## Scripts

Following we describe the usage and scope of the scripts we used to evaluate IoT protocols:

1. `summarize_signature_reconstructed_values_per_app_protocols.py`: We first go over the output files for each protocol that IoTFlow supports and perform some pre-filtering (e.g., we remove arrays of only 0s or artifact values, such as empty parenthesis or single digit numbers).
2. `filter_reconstructed_values_for_URLs.py`: based on some URL regex, we search for URLs in the files we obtained after the initial pre-filtering. Since such regex do not account for AWS endpoints which are prominent among MQTT endpoints, we develop a separate script for this `mqtt_extract_aws_endpoints.py`
3. `get_mqtt_credentials_iotflow.py`: We extract credentials (username and passwords) for MQTT-based apps among the reconstructed values by IoTFlow. We filter based on the name of the function signature (i.e., if it contains the string "username" or "password" respectively, we flag the reconstructed values as credentials). We then perform some manual filtering for invalid or artifact values.
4. `coap_test_connection_2.py` and `coap_test_connection.py`: We probe the two only CoAP endpoints for successful connection.
5. `mqtt_test_connection_2.py`: We then probe MQTT endpoints and note the return code (which tells us why the connection failed).
6. `check_domains_resolving.py`: For XMPP endpoints, we only verify their availability by trying to whois the reconstructed values.
7. Finally, we also report the script we used to compute how many unique companion apps use a specific protocol (we do not account for apps which did not reconstruct any value) with the script `number_of_apps_per_protocol.py`.

Note that, we did perform some manual verification and analysis (e.g., removing some additional artifact values that were recognized as valid by our filters and regex). Simply running the scripts might yield different values. 