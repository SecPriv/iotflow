# Data Flow Analysis

* [FlowDroid bases](libs/) we did not use the latest FlowDroid release as we found bugs that hindered our use: [FlowDroid issue #593](https://github.com/secure-software-engineering/FlowDroid/issues/593), [FlowDroid issue #596](https://github.com/secure-software-engineering/FlowDroid/issues/596). We build the FlowDroid lib from: https://github.com/secure-software-engineering/FlowDroid/tree/542ff865f87a1da5b8fd63ea89ffffa03e6b56e5 .
* [Dockerized](docker/) simplified analysis execution

## Changes to the source code:
* Sources and sink parser with optional location in bytecode, to make it possible only considering specific
* Source and sink manager that only return sources and sinks if the location matches
* Custom Main class and SummaryTaintWrapper to set the custom source/sink parser and manager.