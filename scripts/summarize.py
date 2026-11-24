#!/usr/bin/env python3
"""
Summarise the IoTFlow results of one app as Markdown: run status and errors, endpoints by host,
crypto, UDP/MQTT/WebView values and the data flows found by FlowDroid.

  python3 -I scripts/summarize.py com.coolkit                     # print to the terminal
  python3 -I scripts/summarize.py com.coolkit -o summary.md       # write to a file

Reads VSA/docker/results/ and FlowAnalysis/docker/results/ (change with --vsa / --dfa).
The summary is a starting point for a report: values come from static analysis and still need checking
in the code (e.g. with jadx) before they count as findings.
"""
import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import date
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL_RE = re.compile(r'(?:https?|wss?|mqtts?|tcp|ssl)://[^\s"\'\\<>]{2,200}')
# Hosts that come from XML/schema constants in libraries, not from network requests
NOISE_HOSTS = {"www.w3.org", "w3.org", "java.sun.com", "www.example.org", "example.org", "example.com",
               "xml.org", "xmlpull.org", "apache.org", "www.apache.org", "schemas.android.com",
               "ns.adobe.com", "purl.org", "xml.apache.org", "localhost"}
VSA_ANALYSES = ["endpoints", "crypto", "mqtt", "udp", "webview"]
FLOW_RUNS_ORDER = ["bl_to_icc_or_sink", "bl_from_icc_to_sink", "general_to_icc_or_sink", "general_from_icc_to_sink",
                   "local_to_icc_or_sink", "local_from_icc_to_sink"]


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def value_points(data):
    return (data or {}).get("ValuePoints", []) or []


def short_method(sig, n=90):
    sig = sig or ""
    return sig if len(sig) <= n else sig[:n - 1] + "…"


def flat_values(vp):
    """All string values of a value point's ValueSet."""
    out = []
    for entry in vp.get("ValueSet") or []:
        if isinstance(entry, dict):
            for vals in entry.values():
                out.extend(str(v) for v in (vals if isinstance(vals, list) else [vals]))
    return out


def md_escape(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


# --- sections ----------------------------------------------------------------------------------------

def section_status(pkg, vsa, dfa):
    lines = ["## Run status", "", "**Value set analysis** (`VSA/docker/results/`)", "",
             "| Analysis | Result | Value points | Note |", "|---|---|---|---|"]
    for a in VSA_ANALYSES:
        res = os.path.join(vsa, a, f"{pkg}.json")
        err = os.path.join(vsa, a, f"{pkg}.error")
        data = load_json(res)
        if data is not None:
            note = "forward computation hit its timeout (partial values)" if data.get("TimeoutForwardUsed") == "true" else ""
            lines.append(f"| {a} | ✅ | {len(value_points(data))} | {note} |")
        elif os.path.exists(err):
            first = open(err, errors="replace").readline().strip()
            lines.append(f"| {a} | ❌ error | – | `{md_escape(first[:120])}` |")
        elif os.path.exists(os.path.join(vsa, a, f"{pkg}.timeout")):
            first = open(os.path.join(vsa, a, f"{pkg}.timeout"), errors="replace").readline().strip()
            lines.append(f"| {a} | ⏱ timeout | – | {md_escape(first[:120])} |")
        else:
            lines.append(f"| {a} | – missing | – | timed out, stopped or not run |")

    lines += ["", "**Flow analysis** (`FlowAnalysis/docker/results/`)", "",
              "| FlowDroid run | Status | Flows | Runtime |", "|---|---|---|---|"]
    for run, path in flow_result_files(pkg, dfa):
        state, flows, perf = read_flow_file(path)
        if state is None:
            continue
        t = perf.get("TotalRuntimeSeconds")
        lines.append(f"| {run} | {state} | {len(flows)} | {t + ' s' if t else '–'} |")
    skipped = [a for a in sorted(os.listdir(dfa)) if os.path.isdir(os.path.join(dfa, a))
               and any(os.path.exists(os.path.join(dfa, a, f"{pkg}.vsa-{m}")) for m in ("error", "timeout"))] \
        if os.path.isdir(dfa) else []
    if skipped:
        lines += ["", f"IoTScope analyses skipped in the flow stage because the VSA had to stop them: {', '.join(skipped)}"]
    errors = os.path.join(dfa, "errors", f"{pkg}.log")
    if os.path.exists(errors):
        lines += ["", "**Stopped because of fatal errors** (`results/errors/`, times in UTC):", ""]
        for line in open(errors, errors="replace"):
            if line[:2] == "20":
                lines.append(f"- `{md_escape(line.strip()[:200])}`")
    return lines


OBJ_RE = re.compile(r"[A-Za-z_.$]*Object@[0-9a-f]+")
CLEAN_HOST_RE = re.compile(r"^[a-z0-9.-]+(:\d+)?$", re.I)
# Common top-level domains, to split host names that have text glued onto them ("…shelly.cloudBad")
TLDS = ("com", "net", "org", "cn", "io", "cloud", "de", "at", "eu", "app", "dev", "co", "uk", "us", "gg", "me",
        "tv", "info", "biz", "jp", "kr", "ru", "fr", "it", "es", "nl", "ch", "se", "pl", "in", "br", "tw", "hk", "sg")
# Android emulator addresses of the development machine (e.g. React Native's dev server): not used in releases
EMULATOR_HOSTS = ("10.0.2.2", "10.0.3.2")


def split_glued_tld(host):
    """'control.shelly.cloudbad' -> 'control.shelly.cloud' (None if the host looks normal)."""
    labels = host.split(".")
    if len(labels) < 2 or labels[-1].isdigit() or labels[-1] in TLDS:
        return None
    for tld in sorted(TLDS, key=len, reverse=True):
        if labels[-1].startswith(tld):
            return ".".join(labels[:-1] + [tld])
    return None


def split_url(url):
    """(scheme, authority, rest) after removing simulation placeholders such as java.lang.Object@1a2b."""
    url = OBJ_RE.sub("{obj}", url)
    scheme, _, rest = url.partition("://")
    m = re.match(r"([^/?#$]*)(.*)", rest)
    return scheme.lower(), m.group(1), m.group(2)


def section_endpoints(pkg, vsa, dfa):
    data = load_json(os.path.join(vsa, "endpoints", f"{pkg}.json")) or load_json(os.path.join(dfa, "endpoints", f"{pkg}.json"))
    lines = ["## Endpoints (VSA)", ""]
    if data is None:
        return lines + ["No endpoints result.", ""]
    found = []  # (scheme, authority, url, method)
    for vp in value_points(data):
        for v in flat_values(vp):
            for url in URL_RE.findall(v):
                if "UNKNOWN" in url:
                    continue
                scheme, auth, _ = split_url(url)
                found.append((scheme, auth, OBJ_RE.sub("{obj}", url), vp.get("SootMethod", "")))
    # 1. Split host names with text glued onto the top-level domain ("home.shelly.cloudb" -> "home.shelly.cloud")
    normalized = []  # (scheme, host, glued, url, method)
    for scheme, auth, url, method in found:
        host = auth.lower()
        name, colon, port = host.partition(":")
        fixed = split_glued_tld(name)
        normalized.append((scheme, (fixed or name) + colon + port, bool(fixed), url, method))
    # 2. Reference hosts: well-formed names that were not glued
    clean = {h for _, h, g, _, _ in normalized if not g and CLEAN_HOST_RE.match(h) and ("." in h or h.startswith("192.168."))}
    by_host = defaultdict(lambda: {"urls": set(), "methods": set(), "glued": 0})
    emulator = set()
    for scheme, host, glued, url, method in normalized:
        # 3. Another reference host is a prefix of this one: path or value glued on without a separator
        shorter = max((c for c in clean if c != host and host.startswith(c)), key=len, default=None)
        if shorter:
            host, glued = shorter, True
        elif not glued and host not in clean:
            continue  # not a recognisable host name
        if glued:
            by_host[(scheme, host)]["glued"] += 1
        hostname = host.split(":")[0]
        if not hostname or hostname in NOISE_HOSTS:
            continue
        if hostname in EMULATOR_HOSTS:
            emulator.add(url)
            continue
        by_host[(scheme, host)]["urls"].add(url)
        by_host[(scheme, host)]["methods"].add(method)
    if not by_host:
        return lines + ["No URLs reconstructed.", ""]
    lines += ["Placeholder values (`UNKNOWN`, `{obj}` for simulated objects) and XML/schema constants are left out "
              "or masked. **Plain-text schemes in bold.** \"Glued\" counts URLs where the analysis joined a path "
              "or value onto the host name without a separator (a reconstruction artefact).", "",
              "| Scheme | Host | URLs | Glued | Examples | Code |", "|---|---|---|---|---|---|"]
    for (scheme, host), info in sorted(by_host.items(), key=lambda x: (x[0][1], x[0][0])):
        examples = sorted((u for u in info["urls"] if "{obj}" not in u), key=len)[:3] or sorted(info["urls"], key=len)[:2]
        sch = f"**{scheme}**" if scheme in ("http", "ws", "mqtt", "tcp") else scheme
        methods = sorted(info["methods"])
        lines.append(f"| {sch} | `{host}` | {len(info['urls'])} | {info['glued'] or ''} | "
                     + "<br>".join(f"`{md_escape(u[:110])}`" for u in examples)
                     + " | " + "<br>".join("`" + md_escape(short_method(m, 70)) + "`" for m in methods[:2])
                     + (f" (+{len(methods) - 2})" if len(methods) > 2 else "") + " |")
    if emulator:
        lines += ["", f"Left out: {len(emulator)} URLs to the Android emulator's host address ({', '.join(EMULATOR_HOSTS)}), "
                  "e.g. a React Native development server; such code is normally inactive in release builds."]
    return lines + [""]


def section_values(pkg, vsa, analysis, title, hint):
    data = load_json(os.path.join(vsa, analysis, f"{pkg}.json"))
    lines = [f"## {title}", "", hint, ""]
    if data is None:
        return lines + ["No result.", ""]
    rows = []
    for vp in value_points(data):
        vals = [v for v in flat_values(vp) if v not in ("", "[]", "{}") and "UNKNOWN" not in v]
        if vals:
            rows.append((vp.get("SootMethod", ""), sorted(set(vals))))
    if not rows:
        return lines + ["No values reconstructed.", ""]
    lines += ["| Code | Values |", "|---|---|"]
    for m, vals in sorted(rows):
        shown = ", ".join(f"`{md_escape(v[:80])}`" for v in vals[:6]) + (f" (+{len(vals) - 6})" if len(vals) > 6 else "")
        lines.append(f"| `{md_escape(short_method(m))}` | {shown} |")
    return lines + [""]


def flow_result_files(pkg, dfa):
    files = []
    for path in glob.glob(os.path.join(dfa, "**", f"{pkg}.xml"), recursive=True):
        run = os.path.relpath(os.path.dirname(path), dfa)
        if run in ("local_config",) or run.endswith("_config_to_sink"):
            continue
        files.append((run, path))
    order = {r: i for i, r in enumerate(FLOW_RUNS_ORDER)}
    return sorted(files, key=lambda x: (order.get(x[0], 99), x[0]))


def read_flow_file(path):
    """(TerminationState, set of flows, performance data) of a FlowDroid result; state None if not one."""
    if os.path.getsize(path) == 0:
        return None, set(), {}
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return "unreadable", set(), {}
    if root.tag != "DataFlowResults":
        return None, set(), {}

    def call(e):
        m = re.search(r"<([^>]+)>", e.get("Statement") or "")
        return m.group(1) if m else (e.get("Statement") or "")[:100]

    flows = set()
    for res in root.iter("Result"):
        sink = res.find("Sink")
        for src in res.iter("Source"):
            flows.add((call(src), src.get("Method", ""), call(sink), sink.get("Method", "")))
    pd = root.find("PerformanceData")
    perf = {e.get("Name"): e.get("Value") for e in pd} if pd is not None else {}
    return root.get("TerminationState"), flows, perf


def section_flows(pkg, dfa):
    lines = ["## Data flows (FlowDroid)", "",
             "Source → sink, with the methods they are called in. In the `*_connection` runs the sources are "
             "request/connection objects (`<init>`), which IoTFlow uses to link requests and responses; they are "
             "not data sources.", ""]
    any_flow = False
    for run, path in flow_result_files(pkg, dfa):
        state, flows, _ = read_flow_file(path)
        if not flows:
            continue
        any_flow = True
        lines += [f"### {run} ({state}, {len(flows)} flows)", "", "| Source | in | Sink | in |", "|---|---|---|---|"]
        for s, sm, k, km in sorted(flows, key=lambda f: (f[3], f[1])):
            lines.append(f"| `{md_escape(s.split(': ', 1)[-1][:60])}` | `{md_escape(short_method(sm, 70))}` "
                         f"| `{md_escape(k.split(': ', 1)[-1][:60])}` | `{md_escape(short_method(km, 70))}` |")
        lines.append("")
    if not any_flow:
        lines.append("No flows found.")
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("package", help="package name, e.g. com.coolkit")
    parser.add_argument("-o", "--output", help="write Markdown to this file instead of the terminal")
    parser.add_argument("--vsa", default=os.path.join(ROOT, "VSA", "docker", "results"))
    parser.add_argument("--dfa", default=os.path.join(ROOT, "FlowAnalysis", "docker", "results"))
    args = parser.parse_args()
    pkg = args.package

    if not glob.glob(os.path.join(args.vsa, "*", f"{pkg}.*")) and not glob.glob(os.path.join(args.dfa, "**", f"{pkg}.*"), recursive=True):
        sys.exit(f"No results for {pkg} in {args.vsa} or {args.dfa}")

    out = [f"# IoTFlow summary: `{pkg}`", "", f"Generated {date.today()} by `scripts/summarize.py`. "
           "Static-analysis output: check values in the code before reporting them as findings.", ""]
    out += section_status(pkg, args.vsa, args.dfa) + [""]
    out += section_endpoints(pkg, args.vsa, args.dfa)
    out += section_values(pkg, args.vsa, "crypto", "Cryptography (VSA)",
                          "Algorithms, modes and constant keys/IVs passed to `javax.crypto`. All-zero arrays are often "
                          "buffers filled at runtime, not real keys.")
    out += section_values(pkg, args.vsa, "udp", "UDP (VSA)", "Addresses, ports and payloads of datagram sockets.")
    out += section_values(pkg, args.vsa, "mqtt", "MQTT (VSA)", "Broker URLs, topics and client options.")
    out += section_values(pkg, args.vsa, "webview", "WebView (VSA)", "URLs and content loaded into WebViews.")
    out += section_flows(pkg, args.dfa)

    text = "\n".join(out) + "\n"
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
        print(f"wrote {args.output}")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
