# Dynamic Analysis



## List of Dynamically Tested IoT Devices

| **Device**          | **Type**          | **App Id**                  |
|---------------------|-------------------|-----------------------------|
| Bose QC35           | Headphones        | com.bose.monet              |
| Divoom Timebox      | Alarm clock       | com.divoom.Divoom           |
| Fitbit Inspire 1    | Smart Watch       | com.fitbit.FitbitMobile     |
| Blaupunkt           | Smart Watch       | cn.xiaofengkj.fitpro        |
| HHCC FlowerCare     | Plant Sensor      | com.huahuacaocao.flowercare |
| Hama WiFi           | Light Bulb        | com.hama.smart              |
| Philips Hue         | Light Bulb        | com.signify.hue.blue        |
| Ikea DIRIGERA       | Smart Hub         | com.ikea.tradfri.lighting   |
| Anti-Lost           | Anti-Lost         | com.lenzetech.kindelf       |
| LIFX A60            | Light Bulb        | com.lifx.lifx               |
| Nut Find3           | Anti-Lost         | com.nut.blehunter           |
| Soundcore Life Q35  | Headphones        | com.oceanwing.soundcore     |
| Wiz Colour          | Light Bulb        | com.tao.wiz                 |







## Manual Matching

We extract domains from IoTFlow's reconstructed values using the Python library [tldextract](https://github.com/john-kurkowski/tldextract) while we extract them from the mitmproxy dumps for the dynamic analysis. Further, for paths, we filter out from IoTFlow the values that do not contain a `/`. We repeat this process for each of the 13 apps.

Before starting our evaluation on matching values between statically- and dynamically-obtained ones, we manually filtered out invalid and artifact domains and paths. Specifically, we removed a total of 49 domains (45 from IoTFlow's values and four from traffic captures). We removed mostly localhost domains (127.0.0.1) and analysis artifacts that do not follow the correct domain/IP structure. Further, we removed seven paths from IoTFlow's values as they represented Java classes or null values.


After the pre-filtering, we start with our matching process described in Section 5. We adopt a full-string match to find the exact matching. Despite already yielding results, this approach is not particularly suited in this context as domains and paths might often rely on dynamically generated data (e.g., product codes) that we will not find in our static data. For example, we found the following path while dynamically interacting with the Soundcore app`/v1/speaker/sound_core/A3027/firmware/update` while we statically reconstructed `/v1/speaker/sound_core/Intent\_GetExtra java.lang.String -> "productCode"-[productCode]/firmware/update`.
Thus, a group of three experts individually manually labeled the domains and paths, looking for additional pairs. In case of disagreements, we figured those out till all results converged.




### Table: Manual Matching of Apps
We report the list of the 13 IoT devices with the total numbers of domains and paths we found in the traffic captures (**DA** columns) and reconstructed statically (**IF** columns). Further, the columns **Matches** show the **Exact** and **Manual** matches among the two. We compute the exact matches by performing a full string match and, secondly, manually verify cases where a full match might have failed to identify a valid pair.  Finally, the **IoT related** columns represent the findings we manually labeled IoT related. We report the numbers of IoT-related domains and paths across uniquely IoTFlow's values, uniquely dynamic ones, and shared across the two. For further information about the matching see the spreadsheets in the [domain](domain/) and [path](path/) directories.

|                     |     **Domains** |||||||                                                                                                                    **Paths**   |||||||
|---------------------|-----------------:|-----------------:|--------------------:|---------------------:|-----------------:|-----------------:|-------------------:|-----------------:|-----------------:|--------------------:|---------------------:|-----------------:|-----------------:|-------------------:|
|                     |**Total Values** ||                    **Matches**      ||                       **IoT-Related**|||                                   **Total Values**  ||                     **Matches**     ||                     **IoT-Related**  |||
|         **Device**  |        **IF**   |         **DA**  |         **Exact**  |         **Manual**  | **IF**          | **DA**          | **Both**          |         **IF**  |         **DA**  |         **Exact**  |         **Manual**  |         **IF**  |         **DA**  |         **Both**  |
| Bose QC35           | 14              | 17              | 5                  | 3                   | 2               | 1               | 5                 | 33              | 39              | 4                  | -                   | 11              | 11              | 3                 |
| Divoom Timebox      | 34              | 17              | 3                  | -                   | 6               | 4               | 1                 | 57              | 48              | 4                  | -                   | 37              | 32              | 4                 |
| Fitbit Inspire 1    | 10              | 20              | 3                  | -                   | 1               | 2               | 3                 | 33              | 54              | -                  | 17                  | 11              | 26              | 17                |
| Blaupunkt           | 22              | 14              | 3                  | -                   | -               | -               | 1                 | 29              | 17              | 1                  | -                   | 16              | 6               | 1                 |
| HHCC FlowerCare     | 30              | 7               | 1                  | -                   | 8               | 2               | 1                 | 46              | 4               | -                  | 1                   | 31              | 1               | -                 |
| Hama WiFi           | 8               | 9               | 2                  | -                   | -               | 4               | 1                 | 13              | 9               | 1                  | 1                   | 6               | 4               | 2                 |
| Philips Hue         | 6               | 6               | 4                  | -                   | 1               | -               | 1                 | 26              | 7               | 2                  | 1                   | 1               | 2               | 1                 |
| Ikea DIRIGERA       | 15              | 48              | 2                  | 3                   | 4               | 1               | 1                 | 77              | 51              | 1                  | 1                   | 45              | -               | -                 |
| Anti-Lost           | 3               | 1               | -                  | -                   | -               | -               | -                 | 2               | 1               | -                  | -                   | -               | -               | -                 |
| LIFX A60            | 13              | 26              | 3                  | -                   | 1               | 1               | 2                 | 44              | 34              | 5                  | 3                   | 19              | 10              | 7                 |
| Nut Find3           | 42              | 15              | 5                  | -                   | 10              | -               | 2                 | 54              | 17              | 2                  | 1                   | 8               | 3               | 2                 |
| Soundcore Life Q35  | 8               | 19              | 1                  | -                   | -               | 2               | 1                 | 66              | 39              | 8                  | 5                   | 45              | 8               | 12                |
| Wiz Colour          | 9               | 19              | 4                  | 1                   | -               | 2               | 2                 | 16              | 17              | 2                  | 2                   | 1               | 7               | 1                 |
|        sum          | 214             | 218             | 36                 | 7                   | 33              | 19              | 21                | 496             | 337             | 30                 | 32                  | 231             | 110             | 50                |
|       min           | 3               | 1               | 0                  | 0                   | 0               | 0               | 0                 | 2               | 1               | 0                  | 0                   | 0               | 0               | 0                 |
|       max           | 42              | 48              | 5                  | 3                   | 10              | 4               | 5                 | 77              | 54              | 8                  | 17                  | 45              | 32              | 17                |
|       avg           | 16.46           | 16.77           | 2.77               | 0.54                | 2.54            | 1.46            | 1.62              | 38.15           | 25.92           | 2.31               | 2.46                | 17.77           | 8.46            | 3.85              |




## Unique Domains and Paths
Comparison of unique domains and paths reconstructed to the ones extracted from the network traffic during automatic and manual testing. The Overlap % compares the domains extracted from the manual testing to the ones the VSA found, and Monkey triggered.
The numbers represent *unique* domains and paths *over all apps*.

|               | **IoTFlow**       | **Monkey**      | **Manual Testing**     |
|---------------|-------------------|-----------------|------------------------|
| Total Domains | 152               | 88              | 179                    |
| Overlap (%)   | 35 (19.55%)       | 62 (34.64%)     | 179 (100%)             |
| Total Paths   | 469               | 224             | 736                    |

## Scripts

1. We perform automated tests on the devices using Frida to bypass certificate pinning both using Monkey (`test_monkey_automated.py`) and by manually interacting (`test_manual_automated.py`) with the companion app installed on an Android Pixel phone. We additionally provide the iptables rules we used to forward the traffic to the proxy (`iptables.sh` and `iptables_stop.sh`)
2. After capturing the traffic, we convert mitdumps into txt traffic and extract URLs and paths from mitmproxy traffic for both manual and monkey interactions: `extract_urls_paths_bodies_from_mitmproxy_traffic.py`
3. We extract and filter IoTFlow's URLs and paths: `extract_urls_from_reconstructed_values.py` and `remove_artifacts_from_reconstructed_paths.py`
4. We perform endpoint categories analysis (e.g., Advertisement) for TLDs and full domains for both endpoints collected while manually interacting with the devices and the ones reconstructed by IoTFlow: all the scripts can be found in the folder `endpoint_categories/`
5. We perform full string matching between values reconstructed by IoTFlow and values found in our dynamic traffic capture with mitmproxy `compare_full_match.py`
6. We finally create the CSVs we use for manual analysis: `create_csv.py`