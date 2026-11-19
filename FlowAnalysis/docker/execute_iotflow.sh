#!/bin/sh
# MMF / MMI: max heap (GB) for FlowDroid / each IoTScope JVM; up to two IoTScope JVMs run next to FlowDroid.
# Override via the environment (see compose.yaml), e.g. MMF=30 MMI=12 on a 64 GB machine.
python3 scripts/iotflow.py -a $1 -tfc 450 -tfa 900 -mmf ${MMF:-8} -mmi ${MMI:-4} -sd -o /results/ -br;
python3 scripts/iotflow.py -a $1 -tfc 450 -tfa 900 -mmf ${MMF:-8} -mmi ${MMI:-4} -sd -o /results/ -gr;
python3 scripts/iotflow.py -a $1 -tfc 450 -tfa 900 -mmf ${MMF:-8} -mmi ${MMI:-4} -sd -o /results/ -lr;
