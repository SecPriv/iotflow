#!/bin/sh
python3 scripts/iotflow.py -a $1 -tfc 450 -tfa 900 -mmf 16 -mmi 16 -sd -o /results/ -br;
python3 scripts/iotflow.py -a $1 -tfc 450 -tfa 900 -mmf 16 -mmi 16 -sd -o /results/ -gr;
python3 scripts/iotflow.py -a $1 -tfc 450 -tfa 900 -mmf 16 -mmi 16 -sd -o /results/ -lr;
