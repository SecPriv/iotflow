from xml.etree.ElementTree import Element, tostring
from typing import Optional, List, Dict, Set


class SourceSink:
    def __init__(self, parameters: List[str], base_method: str, return_type: str, stmt_type: str,
                 signature: str, method_name: str):
        self.parameters = parameters
        self.base_method = base_method
        self.return_type = return_type
        self.stmt_type = stmt_type
        self.signature = signature
        self.method_name = method_name


def get_sources_sinks(path):
    result = set()
    with open(path, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line.startswith("%"):
                continue

            result.add(line)

    return result


# _SOURCE_
# _SINK_
# _BOTH_

def add_parameters(parameters: List[str], source_sink_attrib: Dict[str, str], base: Element) -> Element:
    for i in range(0, len(parameters)):
        tmp = Element("param", attrib={"index": str(i), "type": parameters[i]})
        access_path = Element("accessPath", attrib=source_sink_attrib)
        tmp.append(access_path)
        base.append(tmp)

    return base


def add_base(base_method: str, source_sink_attrib: Dict[str, str], base: Element) -> Element:
    tmp = Element("base", attrib={"type": base_method})
    access_path = Element("accessPath", attrib=source_sink_attrib)
    tmp.append(access_path)
    base.append(tmp)
    return base


def add_return(return_type: str, source_sink_attrib: Dict[str, str], return_elem: Element) -> Element:
    tmp = Element("return", attrib={"type": return_type})
    access_path = Element("accessPath", attrib=source_sink_attrib)
    tmp.append(access_path)
    return_elem.append(tmp)
    return return_elem


def add_param_or_base(parameters: List[str], base_method: str, source_sink_attrib: Dict[str, str],
                      elem: Element) -> Element:
    if len(parameters) == 0:
        elem = add_base(base_method, source_sink_attrib, elem)
    else:
        elem = add_parameters(parameters, source_sink_attrib, elem)
    return elem


def get_source_sink_attrib(stmt_type: str) -> Dict[str, str]:
    if "_SOURCE_" in stmt_type:
        return {"isSource": "true", "isSink": "false"}
    elif "_BOTH_" in stmt_type:
        return {"isSource": "true", "isSink": "true"}
    else:
        return {"isSource": "false", "isSink": "true"}


def create_element(parameters: List[str], base_method: str, return_type: str, stmt_type: str,
                   signature: str) -> Element:
    source_sink_attrib = get_source_sink_attrib(stmt_type)
    method_attrib = {"signature": signature}

    if "_SOURCE_" in stmt_type or "_BOTH_" in stmt_type:
        if "callback" in base_method.lower() and return_type == "void":
            method_attrib["callType"] = "callback"
            current_xml_method = Element("method", attrib=method_attrib)
            current_xml_method = add_parameters(parameters, source_sink_attrib, current_xml_method)

        elif return_type == "void":
            current_xml_method = Element("method", attrib=method_attrib)
            current_xml_method = add_base(base_method, source_sink_attrib, current_xml_method)
            if "_BOTH_" in stmt_type:
                current_xml_method = add_parameters(parameters, source_sink_attrib, current_xml_method)
        else:
            current_xml_method = Element("method", attrib=method_attrib)
            current_xml_method = add_return(return_type, source_sink_attrib, current_xml_method)
            if "_BOTH_" in stmt_type:
                current_xml_method = add_param_or_base(parameters, base_method, source_sink_attrib, current_xml_method)
    else:  # SINK
        # assumption - in general params, if no params base
        current_xml_method = Element("method", attrib=method_attrib)
        current_xml_method = add_param_or_base(parameters, base_method, source_sink_attrib, current_xml_method)

    return current_xml_method


def rreplace(s, old, new, count):
    return (s[::-1].replace(old[::-1], new[::-1], count))[::-1]


def parse_source_sink_line(line: str) -> Optional[SourceSink]:
    if "->" in line:
        line_array = line.split("->")
        signature = line_array[0].strip().replace("<", "", 1)
        signature = rreplace(signature, ">", "", 1)
        #signature = signature.replace("<", "&lt;").replace(">", "&gt;")
        source_sink_type = line_array[1].strip()
        if ':' in signature:
            method_array = signature.split(":")
            base_method = method_array[0]
            name_array = method_array[1].strip().split(" ")
            return_value = name_array[0]
            parameter_array = name_array[1].strip().replace(")", "")
            parameter_array = parameter_array.split("(")
            method_name = parameter_array[0]
            if len(parameter_array) != 2:
                print(line)
                return None
            parameters_tmp = parameter_array[1].split(",")
            parameters = []
            for p in parameters_tmp:
                if len(p.strip()) == 0:
                    continue
                parameters.append(p.strip())
            return SourceSink(parameters, base_method, return_value, source_sink_type, signature, method_name)

    return None


def create_element_from_line(line: str) -> Optional[Element]:
    source_sink = parse_source_sink_line(line)
    if source_sink is None:
        return None
    return create_element(source_sink.parameters, source_sink.base_method, source_sink.return_type,
                          source_sink.stmt_type, source_sink.signature)


def to_xml(lines: Set[str]):
    result = Element("sinkSources", attrib={"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                            "xmlns:schemaLocation": "SourcesAndSinks.xsd"})
    category = Element("category",
                       attrib={"id": "NO_CATEGORY", "customId": "WHATEVER", "description": "Something goes here"})
    for line in lines:
        source_sink = parse_source_sink_line(line)
        if source_sink is None:
            continue
        current_xml_method = create_element_from_line(line)
        category.append(current_xml_method)

    result.append(category)
    return result


def to_file(xml_element: Element, path: str) -> None:
    b_xml = tostring(xml_element)

    # Opening a file under the name `items2.xml`,
    # with operation mode `wb` (write + binary)
    with open(path, "wb") as f:
        f.write(b_xml)


def create_xml_config(text_config_path: str, output_path: str) -> None:
    source_sinks = get_sources_sinks(text_config_path)
    xml_sources_sinks = to_xml(source_sinks)
    to_file(xml_sources_sinks, output_path)


