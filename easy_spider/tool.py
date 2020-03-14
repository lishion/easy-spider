import posixpath
from typing import Any
from os import path
import sys


def get_extension(url):
    return posixpath.splitext(url)[-1].lower().lstrip(".")


def get_public_attr(instance: Any):
    for attr, value in instance.__dict__.items():
        if not attr.startswith("_"):
            yield attr


def copy_attr(attr, _from, _to):
    setattr(_to, attr, getattr(_from, attr))


def get_abs_path(file_path):
    return path.dirname(path.abspath(file_path))


ABS_PATH = get_abs_path(__file__)
sys.path.append(path.join(ABS_PATH, ".."))
