import json

from typing import List

# all connections
# iotscope results
from icc_connection import ValuePoint, parse_iotscope




def find_local_communication():
    return


def get_results_from_both():
    return


def get_results_from_source_connection():
    return

# create config
# run flowdroid to icc or sink
# create config
# run flowdroid


def get_method(signature: str):
    signature = signature.strip()
    signature_splitted = signature.split(" ")
    if len(signature_splitted) >= 2:
        result = signature_splitted[2]
        result = result[0: len(result)-1]
        return result

    return signature