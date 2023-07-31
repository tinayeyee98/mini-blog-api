import traceback

from copy import deepcopy
from datetime import datetime
from bson import ObjectId
from uuid import uuid4


def create_http_headers(**kwargs):  # pragma: no cover
    """Create HTTP headers for outbound requests."""
    if "x-request-id" not in kwargs.keys():
        kwargs["x-request-id"] = uuid4().hex

    headers = {
        "content-type": "application/json",
    }
    headers.update(kwargs)
    return headers


def get_exception_context(et, ev, tb):
    exc_context = {
        "error": True,
        "exception.type": str(et.__name__),
        "exception.message": str(ev),
    }
    if tb:
        exc_context["exception.stacktrace"] = traceback.format_exception(
            et, ev, tb)
    return exc_context


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
