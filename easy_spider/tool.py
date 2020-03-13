import posixpath
from typing import Any
from os import path


def get_extension(url):
    return posixpath.splitext(url)[-1].lower().lstrip(".")


def get_public_attr(instance: Any):
    for attr, value in instance.__dict__.items():
        if not attr.startswith("_"):
            yield attr


def copy_attr(attr, _from, _to):
    setattr(_to, attr, getattr(_from, attr))


ABS_PATH = path.dirname(path.abspath(__file__))
