#!/usr/bin/env python3
"""
Find FlowDroid runs that did not finish (e.g. out of memory) and delete their result files, so that the
next pipeline run repeats only those runs. Everything else is skipped by IoTFlow because its result file
exists: VSA results, successful FlowDroid runs.

Dependent results are deleted too: the "<x>_from_icc_config_to_sink" and "<x>_from_icc_to_sink" files are
derived from "<x>_to_icc_or_sink" (x = bl, general, local) and would otherwise be stale.

Dry run by default; --apply deletes.

  python3 -I scripts/reset_incomplete.py                       # list incomplete runs of all apps
  python3 -I scripts/reset_incomplete.py --apply               # delete them
  python3 -I scripts/reset_incomplete.py --apply com.coolkit   # only these packages
  python3 -I scripts/reset_incomplete.py --states DataFlowOutOfMemory,DataFlowTimeout

Then start the pipeline again, e.g. with more memory: MMF=30 MMI=12 setsid nohup scripts/run_pipeline.sh ...
The result files are written by the containers as root; if deleting fails, run the same command with sudo.
"""
import argparse
import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPENDENTS = {f"{x}_to_icc_or_sink": [f"{x}_from_icc_config_to_sink", f"{x}_from_icc_to_sink"]
              for x in ("bl", "general", "local")}


def termination_state(path):
    """TerminationState of a FlowDroid results file; None if it is not one (empty, config, ...)."""
    if os.path.getsize(path) == 0:
        return None
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return "unreadable"
    return root.get("TerminationState") if root.tag == "DataFlowResults" else None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("packages", nargs="*", help="only these packages (default: all)")
    parser.add_argument("--results", default=os.path.join(ROOT, "FlowAnalysis", "docker", "results"),
                        help="FlowAnalysis results folder (default: %(default)s)")
    parser.add_argument("--states", default="DataFlowOutOfMemory",
                        help="comma-separated TerminationStates to reset (default: %(default)s)")
    parser.add_argument("--apply", action="store_true", help="delete the files (default: only list them)")
    args = parser.parse_args()
    states = set(args.states.split(","))

    to_delete = defaultdict(set)  # package -> set of paths
    for dirpath, _, files in os.walk(args.results):
        for name in files:
            if not name.endswith(".xml"):
                continue
            package = name[:-4]
            if args.packages and package not in args.packages:
                continue
            path = os.path.join(dirpath, name)
            state = termination_state(path)
            if state not in states:
                continue
            run = os.path.relpath(dirpath, args.results)
            print(f"{package}: {run} ({state})")
            to_delete[package].add(path)
            for dependent in DEPENDENTS.get(run, []):
                dep_path = os.path.join(args.results, dependent, name)
                if os.path.exists(dep_path):
                    print(f"{package}:   + {dependent} (derived from {run})")
                    to_delete[package].add(dep_path)

    total = sum(len(p) for p in to_delete.values())
    if total == 0:
        print("Nothing to reset.")
        return
    if not args.apply:
        print(f"\n{total} files would be deleted. Run again with --apply to delete them.")
        return
    failed = 0
    for paths in to_delete.values():
        for path in sorted(paths):
            try:
                os.remove(path)
            except PermissionError:
                failed += 1
                print(f"permission denied: {path}", file=sys.stderr)
    print(f"\nDeleted {total - failed} of {total} files.")
    if failed:
        print("The result files belong to root (written by the containers); run the same command with sudo.",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
