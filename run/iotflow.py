import requests
import os
import time
import json
import subprocess
import shutil
import re

from androguard.misc import APK, AnalyzeAPK

from typing import Set, List

from icc_connection import parse_iotscope, parse_flowdroid, create_key_map, create_stmt_map, ValuePoint, \
    parse_flowdroid_local
import argparse
from parse_source_sink_txt_to_xml import create_xml_config, create_element_from_line, to_file
from xml.etree.ElementTree import Element, parse


flowdroid_path = ""
platform = ""
easy_taintwrapper = ""
summary_taintwrapper = ""
dex2jar = ""
iotscope_sources = ""
iotscope_sinks = ""
sources_sinks_from_ble = ""
sinks_from_icc = ""
taintrules = ""
iotscope_path = ""
java = "java"


def has_bl_permission(path: str) -> bool:
    apk = APK(path)
    permissions = apk.get_permissions()
    bl_permission = ["android.permission.BLUETOOTH", "android.permission.BLUETOOTH_ADMIN",
                     "android.permission.BLUETOOTH_ADVERTISE", "android.permission.BLUETOOTH_CONNECT",
                     "android.permission.BLUETOOTH_SCAN"]
    for permission in bl_permission:
        if permission in permissions:
            return True
    print(f"{path} no bluetooth")
    return False


def create_dir_if_not_exists(path: str):
    if os.path.isfile(path) or path.endswith(".json") or path.endswith(".xml"):
        path = os.path.dirname(path)

    if not os.path.exists(path):
        print(path)
        os.makedirs(path, exist_ok=True)


def download_data(fp: str, q: str, output_path: str):
    url = f"http://apk-deguard.com/fetch?fp={fp}&q={q}"

    r = requests.get(url)
    if r.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(r.content)
    return


def create_empty_file(path: str):
    if os.path.exists(path):
        return
    create_dir_if_not_exists(path)
    with open(path, "w"):
        pass
    return


def download_deguard_data(output_path: str, fp: str):
    # 1. create folder
    # 2. download all data
    # return
    print("mapping")
    download_data(fp, "mapping", f"{output_path}_mapping")
    print("src")

    download_data(fp, "src", f"{output_path}_src.zip")
    print("apk")
    download_data(fp, "apk", f"{output_path}_deobfuscated.apk")
    return


def create_result(apk_path):
    directory = os.path.dirname(apk_path)
    filename = os.path.basename(apk_path).replace(".apk", "")
    full_path = os.path.join(directory, filename)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
        shutil.copy2(apk_path, os.path.join(full_path, f"old_{filename}.apk"))
        return True

    return False


def deguard_check_progress(fp: str, output_path: str):
    url = f"http://apk-deguard.com/status?fp={fp}"

    response = requests.get(url)
    if response.status_code != 200:
        print("error")
        return False

    response_json = json.loads(response.text)

    progress = response_json.get("progress", "ERROR")

    if progress == "ERROR" or progress == "READY":
        print("finished")
        download_deguard_data(output_path, fp)
        return False
    else:
        print("result not ready")
        # wait and check again
        return True


def get_package_name(apk_path: str) -> str:
    return os.path.basename(apk_path).replace(".apk", "")


def get_output_prefix(output_path: str, apk_path: str) -> str:
    return os.path.join(output_path, get_package_name(apk_path))


def deobfuscate(output_path: str, apk_path: str):
    deobfuscated_apk = f"{get_output_prefix(output_path, apk_path)}_deobfuscated.apk"
    if os.path.exists(deobfuscated_apk):
        return deobfuscated_apk

    try:
        url = "http://apk-deguard.com/upload"

        payload = open(apk_path, 'rb')
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'http://apk-deguard.com'
        }
        response = requests.post(url, headers=headers, files={"file": (os.path.basename(apk_path), payload)})

        if response.status_code != 200:
            return apk_path

        response_json = json.loads(response.text)

        process_hash = response_json.get("fp", "")
        print(process_hash)

        if process_hash == "":
            return apk_path

        while deguard_check_progress(process_hash, apk_path):
            time.sleep(10)

        if os.path.exists(deobfuscated_apk):
            return deobfuscated_apk
    except requests.exceptions.ConnectionError:
        print("connection aborted")

    return apk_path


def get_full_path(apk_path: str):
    directory = os.path.dirname(apk_path)
    filename = os.path.basename(apk_path).replace(".apk", "").replace("old_", "")
    if filename in directory:
        return directory

    directory = os.path.join(directory, filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory


def get_apk_name(apk_path: str):
    return os.path.basename(apk_path).replace(".apk", "")


def flowdroid_run(apk_path: str, sources_sinks: str, output_path: str, callback_timeout: int,
                  dataflow_analysis_timeout: int, max_memory: int, summary_taint_wrapper: str, easy_taint_wrapper: str,
                  timeout: int):

    if os.path.exists(output_path):
        return
    create_dir_if_not_exists(output_path)

    command = ["timeout", "--foreground", f"--kill-after={timeout}m", f"{timeout}m", f"{java}", "-jar",
               f"-Xms{max_memory - 2}g", f"-Xmx{max_memory}g", f"{flowdroid_path}", "-a",
               f"{apk_path}", "-d", "-s", f"{sources_sinks}", "-p", f"{platform}", "-cs", "SOURCELIST",
               "-l", "NONE", "-ol", "-o", f"{output_path}", "-tw", "MULTI", "-t", f"{summary_taint_wrapper}", "-t",
               f"{easy_taint_wrapper}"]
    if callback_timeout is not None:
        command.append("-ct")
        command.append(str(callback_timeout))
    if dataflow_analysis_timeout is not None:
        command.append("-dt")
        command.append(str(dataflow_analysis_timeout))
    print(command)
    process = subprocess.Popen(command)
    return process


def run_iotscope(apk_path: str, sink_path: str, output_path: str, max_memory: int, timeout: int):
    if os.path.exists(output_path):
        return
    create_dir_if_not_exists(output_path)

    command = ["timeout", "--foreground", f"--kill-after={timeout}m", f"{timeout}m", f"{java}", "-jar",
               f"-Xmx{max_memory}g",
               f"{iotscope_path}", "-d", f"{sink_path}", "-a", f"{apk_path}",
               "-p", f"{platform}", "-dj", f"{dex2jar}", "-t", f"{taintrules}", "-do", "-o", f"{output_path}"]
    process = subprocess.Popen(command)
    return process


def change_to_xml_config(config_path: str) -> str:
    if not config_path.endswith(".txt"):
        return config_path

    xml_path = config_path.replace(".txt", ".xml")
    if os.path.exists(xml_path):
        return xml_path

    create_xml_config(config_path, xml_path)
    return xml_path


def analysis_to_icc(apk_path: str, args, config, output_path):
    processes = []
    processes.append(run_iotscope(apk_path, iotscope_sources,
                                  f"{args.output_path}/sources/{get_package_name(args.apk_path)}.json",
                                  args.max_memory_iotscope, args.timeout))
    processes.append(run_iotscope(apk_path, iotscope_sinks,
                                  f"{args.output_path}/sinks/{get_package_name(args.apk_path)}.json",
                                  args.max_memory_iotscope, args.timeout))
    processes.append(
        flowdroid_run(apk_path, config, output_path,
                      args.timeout_flowdroid_callbacks, args.timeout_flowdroid_analysis, args.max_memory_flowdroid,
                      args.summary_taint_wrapper, args.easy_taint_wrapper, args.timeout))

    for p in processes:
        if p is not None:
            p.wait()


def create_config(template, output_path, result: Set[ValuePoint]):
    elements = []
    for k, v in create_stmt_map(result).items():
        if len(v) == 0:
            continue

        current_source = f"{k} -> _SOURCE_"
        current_element = create_element_from_line(current_source)

        fixed_location = Element("fixedLocation")

        for locations in v:
            current_location = Element("location", {"methodSignature": locations.parent_method,
                                                    "lineNumber": str(locations.line_number)})
            fixed_location.append(current_location)

        current_element.append(fixed_location)

        elements.append(current_element)

    xml_template: Element = parse(template).getroot()
    category = xml_template.find("category")
    for element in elements:
        category.append(element)

    to_file(xml_template, output_path)
    return output_path


def create_icc_config(template, sources, sinks, flowdroid_run, config_path):
    result = set()
    create_dir_if_not_exists(config_path)

    sources = parse_iotscope(sources)
    sinks = parse_iotscope(sinks)
    flowdroid_sinks = parse_flowdroid(flowdroid_run, set(sinks))

    source_map = create_key_map(sources)

    for sink in flowdroid_sinks:
        if sink is None:
            continue
        for key in sink.keys:
            source = source_map.get(key)
            if source is not None:
                result.update(source)

    return create_config(template, config_path, result), len(result) > 0


def create_local_config(template, local_value_points, connection_runs, config_path):
    create_dir_if_not_exists(config_path)
    flowdroid_sinks = set()
    for connection_run in connection_runs:
        if "sink_connection" in connection_run:
            continue
        try:
            tmp = parse_flowdroid_local(connection_run, set(local_value_points))
            flowdroid_sinks.update(tmp)
        except FileNotFoundError:
            print(f"{connection_run} not found")

    return create_config(template, config_path, flowdroid_sinks)


def flowdroid_from_icc(apk_path: str, args, first_flow_run: str, config_path: str, output_path: str, template: str):
    sources = f"{args.output_path}/sources/{get_package_name(apk_path)}.json"
    sinks = f"{args.output_path}/sinks/{get_package_name(apk_path)}.json"
    if os.path.exists(output_path):
        print(f"does already exist {output_path}")
        return
    xml_config = change_to_xml_config(template)

    try:
        config_path, has_result = create_icc_config(xml_config, sources, sinks, first_flow_run, config_path)
        if not has_result:
            print("no icc source found")
            create_empty_file(output_path)
            return

        process = flowdroid_run(apk_path, config_path, output_path,
                                args.timeout_flowdroid_callbacks, args.timeout_flowdroid_analysis,
                                args.max_memory_flowdroid, args.summary_taint_wrapper, args.easy_taint_wrapper,
                                args.timeout)
        if process is not None:
            process.wait()
    except FileNotFoundError:
        print(f"{first_flow_run} not found")


def do_connection_run(xml_path, class_names):
    xml_template: Element = parse(xml_path).getroot()
    category = xml_template.findall("category")
    for category in category:
        for method in category.findall("method"):
            method_signature = method.get("signature")
            params = method.findall("param") + method.findall("base") + method.findall("return")
            # print(len(params))
            for param in params:
                access_path = param.find("accessPath")
                if access_path.get("isSource") == "true":
                    if ':' in method_signature:
                        class_name = method_signature.split(":")[0]
                        class_name = class_name.replace(".", "/")
                        for c in class_names:
                            if class_name in c:
                                print(f"{class_name} in {c}: running connection run")
                                return True
    return False


def connection_runs(args, apk):
    output_paths = []
    connection_runs = []
    connection_runs.append("both/web_apache.xml")
    connection_runs.append("both/web_okhttp3.xml")
    connection_runs.append("both/web_udp_data.xml")

    connection_runs.append("sink_connection/amqp_rabbitmq.xml")
    connection_runs.append("sink_connection/coap_californium.xml")
    connection_runs.append("sink_connection/mqtt_aws.xml")
    connection_runs.append("sink_connection/mqtt_fusesource.xml")
    connection_runs.append("sink_connection/mqtt_paho.xml")
    connection_runs.append("sink_connection/mqtt_tuya.xml")
    connection_runs.append("sink_connection/web_java.xml")

    connection_runs.append("source_connection/amqp_rabbitmq.xml")
    connection_runs.append("source_connection/coap_californium.xml")
    connection_runs.append("source_connection/mqtt_aws.xml")
    connection_runs.append("source_connection/mqtt_fusesource.xml")
    connection_runs.append("source_connection/mqtt_paho.xml")
    connection_runs.append("source_connection/mqtt_tuya.xml")
    connection_runs.append("source_connection/web_java.xml")

    _, _, androguard_analysis = AnalyzeAPK(apk)
    classes = androguard_analysis.get_classes()
    classNames = set()
    for c in classes:
        classNames.add(c.name)

    for config in connection_runs:
        xml_config = change_to_xml_config(f"/home/dschmidt/config/{config}")

        output_path_result = f"{args.output_path}/{config.split('/')[0]}/{config.split('/')[1].replace('.xml', '')}/{get_package_name(args.apk_path)}.xml"
        if not do_connection_run(xml_config, classNames):
            create_empty_file(output_path_result)
            continue

        process = flowdroid_run(apk, xml_config, output_path_result,
                                args.timeout_flowdroid_callbacks, args.timeout_flowdroid_analysis,
                                args.max_memory_flowdroid, args.summary_taint_wrapper, args.easy_taint_wrapper,
                                args.timeout)
        if process is not None:
            process.wait()

        output_paths.append(output_path_result)
    return output_paths


def has_UPNP(jsonData):
    if 'ValuePoints' in jsonData:
        for vp in jsonData['ValuePoints']:
            if 'UsesPotentiallyUPnP' in vp:
                print(jsonData['pname'])
                return True

    return False


def is_app_using_UPNP(app):
    return has_UPNP(app.amqp) or has_UPNP(app.coap) or has_UPNP(app.endpoints) or has_UPNP(app.mqtt) or has_UPNP(
        app.telnet) or has_UPNP(app.xmpp)


def has_local_address(value: str) -> bool:
    for comma in value.split(","):
        for v in comma.split('||'):
            v = v.replace('NOT_FOUND', '')
            v = v.replace('.json', '')
            v = v.replace('.html', '')
            v = v.replace('.php', '')
            v = v.replace('.jpg', '')
            v = v.replace('.png', '')
            v = v.replace('.cgi', '')
            v = v.replace('.aspx', '')
            v = v.replace('.asp', '')
            v = v.replace('.smp', '')
            v = v.replace('.xml', '')
            v = v.replace('.cfg', '')
            v = v.lower()

            local_network = re.findall(
                "(192\.168\.\d\d?\d?\.\d\d?\d?)|(10\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?)|(172\.1[6-9]\.\d\d?\d?\.\d\d?\d?)|(172\.2[0-9]\.\d\d?\d?\.\d\d?\d?)|(172\.3[0-1]\.\d\d?\d?\.\d\d?\d?)|(.*[^:]fromui\.local[:\/ ])|(fd00:)|(fe80:)|(fc00:)",
                v)
            if local_network is not None:
                for finding in local_network:
                    for local in finding:
                        local = local.replace(':', '')
                        local = local.replace('/', '')
                        local = local.replace('https', '')
                        local = local.replace('http', '')

                        if local.startswith("f") and "from" not in local:
                            local = local + ":"

                        if len(local) > 2:
                            if ("fromui.local" not in local or (
                                    "fromui.local" in local and len(local) == len("fromui.local"))):
                                return True
    return False


def can_be_valid(ip_string: str) -> bool:
    ip_string = ip_string.strip()
    splitted_ip = ip_string.split(".")
    if len(splitted_ip) != 4:
        return False

    for item in splitted_ip:
        if int(item) < 0 or int(item) > 255:
            return False

    return True


def has_multicast(value: str) -> bool:
    multicast_addresses = ['255.255.255.255', '224.0.0.', '224.0.1.', '224.0.2.', '224.1.', '224.3.', '224.4.', '225.',
                           '226.',
                           '227.', '228.', '229.', '230.', '231.', '232.', '233.', '234.', '235.', '236.', '237.',
                           '238.', '239.',
                           'ffx0:', 'ffx1:', 'ffx2:', 'ffx3:', 'ffx4:', 'ffx5:', 'ffx6:', 'ffx7:', 'ffx8:', 'ffx9:',
                           'ffxa:',
                           'ffxb:', 'ffxc:', 'ffxd:', 'ffxe:', 'ff02:', 'ff0x:']

    for address in multicast_addresses:
        ip_extract = re.findall(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', value)
        ip_extract2 = re.findall(
            r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))',
            value)
        if len(ip_extract) > 0:
            for c in ip_extract:
                if '127.0.0.1' in c or not can_be_valid(c):
                    continue
                if c.startswith(address):
                    return True
        elif len(ip_extract2) > 0:
            if len(ip_extract2[0]) > 0:
                return True

    return False


def get_local_value_points(data: List[ValuePoint]):
    result = set()
    for value_point in data:
        for value in value_point.keys:
            value = str(value)
            value = value.lower()
            if has_multicast(value):
                result.add(value_point)
                break
            elif has_local_address(value):
                result.add(value_point)
                break
            # TODO: maybe add UPNP -> look at results
    return result


def iot_scope_runs(apk, args):
    output_paths = []
    configs = []
    configs.append("amqp.json")
    configs.append("coap.json")
    configs.append("mqtt.json")
    configs.append("endpoints.json")
    configs.append("xmpp.json")
    configs.append("udp.json")
    configs.append("webview.json")


    for config in configs:
        output = f"{args.output_path}/{config.replace('.json', '')}/{get_package_name(args.apk_path)}.json"
        process = run_iotscope(apk, f"/home/dschmidt/config/iotscope/{config}",
                               output,
                               args.max_memory_iotscope, args.timeout)
        if process is not None:
            process.wait()

        output_paths.append(output)

    return output_paths


def local_run(apk, args):
    first_run_output = f"{args.output_path}/local_to_icc_or_sink/{get_package_name(args.apk_path)}.xml"
    from_icc_to_sink_config = f"{args.output_path}/local_from_icc_config_to_sink/{get_package_name(args.apk_path)}.xml"
    from_icc_to_sink = f"{args.output_path}/local_from_icc_to_sink/{get_package_name(args.apk_path)}.xml"

    connection_run_results = connection_runs(args, apk)
    iot_scope_results = iot_scope_runs(apk, args)
    local_value_points = set()
    for result in iot_scope_results:
        try:
            iotscope_result = parse_iotscope(result)
            tmp_value_points = get_local_value_points(iotscope_result)
            local_value_points.update(tmp_value_points)
        except FileNotFoundError:
            print(f"{result} not found")

    template = args.iotflow_local_config
    config_path = f"{args.output_path}/local_config/{get_package_name(args.apk_path)}.xml"

    if len(local_value_points) == 0:
        print("no local value points")
        create_empty_file(first_run_output)
        create_empty_file(from_icc_to_sink_config)
        create_empty_file(from_icc_to_sink)
        return

    local_config = create_local_config(template, local_value_points, connection_run_results, config_path)

    analysis_to_icc(apk, args, local_config, first_run_output)
    print("local to icc run done")
    flowdroid_from_icc(apk, args, first_run_output, from_icc_to_sink_config, from_icc_to_sink, args.iotflow_template)
    print("local complete run finished")


def bluetooth_run(apk, args):
    bluetooth_config = change_to_xml_config(args.iotflow_bluetooth_sources)
    first_run_output = f"{args.output_path}/bl_to_icc_or_sink/{get_package_name(args.apk_path)}.xml"
    from_icc_to_sink_config = f"{args.output_path}/bl_from_icc_config_to_sink/{get_package_name(args.apk_path)}.xml"
    from_icc_to_sink = f"{args.output_path}/bl_from_icc_to_sink/{get_package_name(args.apk_path)}.xml"

    if not has_bl_permission(apk):
        create_empty_file(first_run_output)
        create_empty_file(from_icc_to_sink_config)
        create_empty_file(from_icc_to_sink)
        return

    analysis_to_icc(apk, args, bluetooth_config, first_run_output)
    print("bl to icc run done")
    flowdroid_from_icc(apk, args, first_run_output, from_icc_to_sink_config, from_icc_to_sink, args.iotflow_template)
    print("bl complete run finished")


def general_run(apk, args):
    general_config = change_to_xml_config(args.iotflow_general_config)
    first_run_output = f"{args.output_path}/general_to_icc_or_sink/{get_package_name(args.apk_path)}.xml"
    from_icc_to_sink_config = f"{args.output_path}/general_from_icc_config_to_sink/{get_package_name(args.apk_path)}.xml"
    from_icc_to_sink = f"{args.output_path}/general_from_icc_to_sink/{get_package_name(args.apk_path)}.xml"

    analysis_to_icc(apk, args, general_config, first_run_output)
    print("general to icc run done")
    flowdroid_from_icc(apk, args, first_run_output, from_icc_to_sink_config, from_icc_to_sink, args.iotflow_template)
    print("general complete run finished")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--apk-path", help="Path to apk file", type=str)
    parser.add_argument("-tfc", "--timeout-flowdroid-callbacks", help="Path to apk file", type=int, default=600)
    parser.add_argument("-tfa", "--timeout-flowdroid-analysis", help="Path to apk file", type=int, default=300)

    parser.add_argument("-mmf", "--max-memory-flowdroid", help="Max memory for the flowdroid vm in g", type=int,
                        default=32)
    parser.add_argument("-mmi", "--max-memory-iotscope", help="Max memory for the flowdroid vm in g", type=int,
                        default=12)

    parser.add_argument("-ibs", "--iotflow-bluetooth-sources", help="Path to the iotflow bluetooth source", type=str,
                        default=sources_sinks_from_ble)
    parser.add_argument("-it", "--iotflow-template", help="Path to the iotflow template", type=str,
                        default=sinks_from_icc)

    parser.add_argument("-igc", "--iotflow-general-config", help="Path to the iotflow bluetooth source", type=str,
                        default="/home/dschmidt/config/general.xml")
    parser.add_argument("-ilc", "--iotflow-local-config", help="Path to the iotflow bluetooth source", type=str,
                        default="/home/dschmidt/config/local.xml")

    parser.add_argument("-sd", "--skip-deobfuscation", help="Skip the deobfuscation step", action='store_true')

    parser.add_argument("-st", "--summary-taint-wrapper", help="Skip the deobfuscation step", type=str,
                        default=summary_taintwrapper)
    parser.add_argument("-et", "--easy-taint-wrapper", help="Skip the deobfuscation step", type=str,
                        default=easy_taintwrapper)
    parser.add_argument("-t", "--timeout", help="Skip the deobfuscation step", type=int,
                        default=60)

    parser.add_argument("-o", "--output-path", help="Skip the deobfuscation step", type=str,
                        default="./output/")

    parser.add_argument("-br", "--bluetooth-run", help="", action='store_true')
    parser.add_argument("-lr", "--local-run", help="", action='store_true')
    parser.add_argument("-gr", "--general-run", help="", action='store_true')

    args = parser.parse_args()
    apk = args.apk_path
    print(f"start analyzing {apk}")
    if not args.skip_deobfuscation:
        apk = deobfuscate(args.output_path, apk)
        print("deobfuscation done")
    elif os.path.exists(f"{get_output_prefix(args.output_path, apk)}_deobfuscated.apk"):
        apk = f"{get_output_prefix(args.output_path, apk)}_deobfuscated.apk"

    if args.bluetooth_run:
        bluetooth_run(apk, args)
    elif args.local_run:
        local_run(apk, args)
    elif args.general_run:
        general_run(apk, args)
    else:
        bluetooth_run(apk, args)
        local_run(apk, args)
        general_run(apk, args)


if __name__ == '__main__':
    main()


