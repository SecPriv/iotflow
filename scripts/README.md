# Scripts

## Running IoTFlow

| Script | What it does |
|---|---|
| `apk2jar.sh <apk>` | Converts an APK to the jar the VSA uses for simulation, one DEX file at a time, and puts it into both `apps_to_analyze/jarFiles/` folders. Run it for every app before starting the containers (dex2jar fails on some large multi-DEX APKs when given the whole APK). |
| `run_pipeline.sh` | Runs the VSA, then the flow analysis (services `vsa` and `dfa` of the top-level `compose.yaml`) on everything in `*/docker/apps_to_analyze/`, detached from the terminal: `setsid nohup scripts/run_pipeline.sh > /dev/null 2>&1 &`. The containers run as the calling user, so results belong to you. Between the stages it copies the VSA's endpoints/mqtt/udp results to the flow stage, which then skips them. Progress in `apps/pipeline.log`, logs in `apps/vsa_run.log`, `apps/dfa_run.log` and `apps/build.log`. Settings via environment variables (see the Docker READMEs), e.g. `MMF=12 setsid nohup scripts/run_pipeline.sh ...`. |
| `reset_incomplete.py` | Lists FlowDroid runs that did not finish (default: `DataFlowOutOfMemory`) and, with `--apply`, deletes their result files and the files derived from them. The next pipeline run then repeats only those runs, e.g. with more memory on a larger machine; everything else is skipped because its results exist. `python3 -I scripts/reset_incomplete.py [--apply] [--states ...] [packages]` (needs `sudo` if the results belong to root). |
| `summarize.py <package>` | Markdown summary of one app's results: run status and stopped analyses, endpoints by host (plain-text schemes in bold, reconstruction artefacts grouped), crypto/UDP/MQTT/WebView values, all FlowDroid flows. `python3 -I scripts/summarize.py com.coolkit -o summary.md`. The starting point for a report; values still need checking in the code. |
| `vsa_version.sh status\|4.4\|4.7` | Switches the VSA used by both stages between the current version (Soot 4.4.1) and the port to Soot 4.7.1 (`dependencies/vsa-soot-4.7/`); keeps a copy of the other. Only when no analysis is running. |

The analysis code itself runs inside the Docker images:
- VSA: `VSA/docker/execute_vsa.sh` (calls `vsa.jar`)
- Flow analysis: `FlowAnalysis/docker/scripts/iotflow.py` (calls FlowDroid and `vsa.jar`), started by `FlowAnalysis/docker/execute_iotflow.sh`

**Running `iotflow.py` without Docker:** the tool paths are constants at the top of `FlowAnalysis/docker/scripts/iotflow.py` (`flowdroid_path`, `platform`, `iotscope_path`, the config paths, ...), all pointing to `/analysis/...` inside the image. Point them to your local copies of `FlowAnalysis/docker/iotflow.jar`, `FlowAnalysis/docker/dependencies/` and `FlowAnalysis/docker/config/`, install `requirements.txt`, and use Java 17. (An older, separate copy of these scripts in `scripts/run/` was removed on 2026-11-19; it had not received any of the fixes.)

## Evaluation

Python scripts and notebooks to [parse and further evaluate](evaluation/) VSA and flow-analysis results, as used for the paper. Python version used: 3.8, Jupyter 6.5.4.
