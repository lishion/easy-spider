import posixpath
from typing import Any
from os import path, remove
import sys
import pickle
from uuid import uuid1
from datetime import datetime


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


def pickle_dump(obj, file_uri):
    with open(file_uri, 'wb') as wd:
        pickle.dump(obj, wd)


def pickle_load(file_uri):
    with open(file_uri, 'rb') as rd:
        return pickle.load(rd)


def uuid():
    return str(uuid1())


def formatted_datetime(fmt=None):
    return datetime.utcnow().strftime(fmt or '%Y-%m-%d %H:%M:%S.%f')


def delete_file(uri):
    try:
        remove(uri)
    except IOError as e:
        # console_logger.warning("delete spill file %s error" % uri)
        # file_logger.warning("delete spill file %s error" % uri, exc_info=True)
        pass


def get_type_name(instance):
    return instance.__class__.__name__


ABS_PATH = get_abs_path(__file__)
sys.path.append(path.join(ABS_PATH, ".."))
EXE_PATH = path.dirname(path.abspath(__name__))


def work_path_join(arg, *args):
    return path.join(EXE_PATH, '.easy-spider', arg, *args)
