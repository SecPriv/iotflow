import json
import xmltodict
from typing import Set


class ValuePoint:
    stmt: str = ""
    parent_method: str = ""
    line_number: int = -1
    keys = set()

    def __init__(self, stmt, parent_method, keys, line_number):
        self.stmt = stmt
        self.parent_method = parent_method
        self.keys = keys
        self.line_number = line_number
        self.value_scope_results = None


    def set_source_values(self, value_scope_results):
        self.value_scope_results = value_scope_results


    def __str__(self):
        return f"ICC(stmt: {self.stmt}, parent_method: {self.parent_method}, keys {self.keys}, line_number {self.line_number})"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.parent_method, self.line_number))

    def __eq__(self, other):
        if other is None:
            return False
        return (self.parent_method, self.line_number) == (other.parent_method, other.line_number)

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)


def create_stmt_map(icc_list):
    result = {}
    for icc in icc_list:
        if icc is None:
            continue
        key = icc.stmt[icc.stmt.index("<"):icc.stmt.index(">") + 1]
        current_list = result.get(key, set())
        current_list.add(icc)
        result[key] = current_list

    return result


def parse_iotscope(path):
    result = []
    try:
        with open(path, "r") as f:
            json_data = json.load(f)
            for vp in json_data.get("ValuePoints", []):
                values: Set[str] = set()
                for vs in vp.get("ValueSet", []):
                    for value in vs.values():
                        for item in value:
                            values.add(item)

                icc_result = ValuePoint(vp.get("Unit", ""), vp.get("SootMethod", ""), values, vp.get("startLineNumber", -1))
                result.append(icc_result)
    except json.decoder.JSONDecodeError:
        pass
    return result


def create_sink_map(icc_sinks):
    result = {}
    for s in icc_sinks:
        if type(s) is type(ValuePoint("", "", "", -1)):
            result[f"{s.parent_method};{s.line_number}"] = s
        else:
            print("error")
    return result


def parse_flowdroid(path, icc_sink_result_set):
    flows = set()
    iotflow_result = None
    icc_sink_result_set = create_sink_map(icc_sink_result_set)

    # load stmt if key is not available look at the icc
    with open(path, "r") as xml_obj:
        # coverting the xml data to Python dictionary
        iotflow_result = xmltodict.parse(xml_obj.read())
        # closing the file
        xml_obj.close()
    if iotflow_result is not None:
        # print(json.dumps(iotflow_result))
        flow_result = iotflow_result.get("DataFlowResults", {})
        results = flow_result.get("Results", {})
        all_results = results.get("Result", [])
        if type(all_results) is not type([]):
            all_results = [all_results]
        for result in all_results:
            sink = result.get("Sink", {})
            sources = result.get("Sources", {})
            current = get_value_point(sink)
            # print(current)
            current = icc_sink_result_set.get(f"{current.parent_method};{current.line_number}")
            flows.add(current)
    return flows


def get_value_point(flowdroid_statement):
    statement = flowdroid_statement.get("@Statement", "<>")
    if "<" in statement and ">" in statement:
        statement = statement[statement.index("<"): statement.index(">") + 1]
    parent_method = flowdroid_statement.get("@Method", "")
    line_number = flowdroid_statement.get("@LineNumber", -1)
    return ValuePoint(statement, parent_method, set(), line_number)


def parse_flowdroid_local(path, local_sources):
    flows = set()
    source_map = create_sink_map(local_sources)

    # load stmt if key is not available look at the icc
    with open(path, "r") as xml_obj:
        # coverting the xml data to Python dictionary
        iotflow_result = xmltodict.parse(xml_obj.read())
        # closing the file
        xml_obj.close()
    if iotflow_result is not None:
        # print(json.dumps(iotflow_result))
        flow_result = iotflow_result.get("DataFlowResults", {})
        results = flow_result.get("Results", {})
        all_results = results.get("Result", [])
        if type(all_results) is not type([]):
            all_results = [all_results]
        for result in all_results:
            # print(result)
            sink = result.get("Sink", {})
            sources = result.get("Sources", {})
            current_sink = get_value_point(sink)
            all_sources = sources.get("Source", [])
            if type(all_sources) is not type([]):
                all_sources = [all_sources]
            for source in all_sources:
                current_source = get_value_point(source)
                if f"{current_source.parent_method};{current_source.line_number}" in source_map:
                    flows.add(current_sink)
    return flows


# icc_sink = parse_iotscope(
#    "/home/david/Desktop/TU/phd/gitlabSecPriv/valuescope/valuesetResult/sink_cn.xiaofengkj.fitpro_linenumber.json")

# icc_source = parse_iotscope(
#    "/home/david/Desktop/TU/phd/gitlabSecPriv/valuescope/valuesetResult/source_cn.xiaofengkj.fitpro_linenumber.json")


def create_key_map(icc_list):
    # reconstructed key - icc object
    keys = {}
    for icc in icc_list:
        for key in icc.keys:
            current = keys.get(key, list())
            current.append(icc)
            keys[key] = current

    return keys


def create_key(icc):
    return f"{icc.stmt}-{icc.parent_method}-{icc.line_number}"


def match_icc(source_to_icc, icc_to_sink):
    matches = {}
    # reconstructed_key-method:
    source_keys = create_key_map(source_to_icc)
    sink_keys = create_key_map(icc_to_sink)

    for source in source_to_icc:
        key = create_key(source)
        current = matches.get(key, list())
        current = set(current)
        for icc_key in source.keys:
            for match in sink_keys.get(icc_key, list()):
                current.add(create_key(match))

        matches[key] = list(current)

    return matches


if __name__ == "__main__":
    parse_flowdroid_local("/home/david/Downloads/allterco.bg.shelly.xml", [])
