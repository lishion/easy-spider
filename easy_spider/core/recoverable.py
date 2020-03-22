from abc import ABC, abstractmethod
from os.path import exists, join
from typing import List
from easy_spider.tool import pickle_load, pickle_dump


class Recoverable(ABC):

    @abstractmethod
    def stash(self, resource): pass

    @abstractmethod
    def recover(self, resource): pass

    @classmethod
    def recover_name(cls): return cls.__name__

    @abstractmethod
    def can_recover(self, resource): pass


class FileBasedRecoverable(Recoverable, ABC):
    """
        利用 pickle 对爬虫进行保存
        子类只需要实现 stash_attr_names，给出需要保存的 attr
        对于需要保存的所有 attr，会形成字典 {attr1, value1, ..., } 并利用 pickle 保存
        恢复时使用 setattr 恢复
    """
    def __init__(self):
        self._stash_attr_names = self.stash_attr_names()
        for attr in self._stash_attr_names:
            self._check_stash_attr(attr)

    @classmethod
    def recover_name(cls):
        return super().recover_name() + ".pickle"

    def _check_stash_attr(self, attr):
        if attr not in self.__dict__:
            raise AttributeError("can't find stash attr `{}`".format(attr))

    @abstractmethod
    def stash_attr_names(self) -> List[str]: pass

    def can_recover(self, resource):
        return exists(self._get_stash_file_uri(resource))

    def _get_stash_file_uri(self, resource):
        return join(resource, self.recover_name())

    def stash(self, resource):
        """
        将需要保存的 attr 存放到 {resource}/{self.__class__.__name__}.pickle
        :param resource: 存放文件路径
        :return: None
        """
        attrs_to_stash = {attr: value for attr, value in self.__dict__.items() if attr in self._stash_attr_names}
        pickle_dump(attrs_to_stash, self._get_stash_file_uri(resource))

    def recover(self, resource):
        """
        从 {resource}/{self.__class__.__name__}.pickle 中恢复
        :param resource: 存放文件路径
        :return: None
        """
        attrs_to_stash = pickle_load(self._get_stash_file_uri(resource))
        for attr, value in attrs_to_stash.items():
            setattr(self, attr, value)

# class BufferedRecoverable(ABC):
#
#     @abstractmethod
#     def write(self): pass
#
#     @abstractmethod
#     def recover(self): pass

