from copy import deepcopy
from datetime import datetime

from bson import ObjectId


def strtolist(string):
    li = list(string.split(","))
    return li


def dt2str(dt):
    # dtfmt = '{:%Y-%m-%d %H:%M:%S}'
    return dt.isoformat() + "Z"


def sanitize(keyval):
    if isinstance(keyval, str):
        return keyval
    if isinstance(keyval, list):
        keyval = [sanitize(each) for each in keyval]
    if isinstance(keyval, dict):
        cp_keyval = deepcopy(keyval)
        for key, val in cp_keyval.items():
            if isinstance(val, ObjectId):
                val = str(val)
            if isinstance(val, datetime):
                val = dt2str(val)
            if "." in key:
                keyval.pop(key)
                key = key.replace(".", "_")
            if isinstance(val, dict):
                val = sanitize(val)
            if isinstance(val, list):
                val = [sanitize(each) for each in val]
            keyval[key] = val
    return keyval
