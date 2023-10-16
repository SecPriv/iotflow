#!/bin/sh
find /apps_to_analyze/ -name "*.apk" ! -name "*.split.*" -maxdepth 1 -print -exec sh execute_iotflow.sh {}  \;
