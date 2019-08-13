"""Includes MetaTracker to track definition order of class attributes."""
from collections import OrderedDict
from abc import ABCMeta


class PublicOrderedDict(OrderedDict):
    """Supplies `public` function to return copy with only keys that are not inclosed in double underscores"""
    def public(self):
        """Returns copy with only keys that are not inclosed in double underscores"""
        return OrderedDict((key, value) for key, value in self.items() if not (key[:2] + key[-2:]) == '____')


class MetaTracker(ABCMeta):
    """Meta class to track attributes of some type in order of declaration

    Example
    -------
    >>> class OrderedInts(metaclass=MetaTracker):
    ...     a = 14
    ...     b = 21
    ...     c = 42
    ... OrderedInts(a=0).__tracked__
    OrderedDict([('__module__', '__main__'), ('__qualname__', 'OrderedInts'), ('a', 0), ('b', 21), ('c', 42)])

    Note
    ----
    See PEP3115

    """
    @classmethod
    def __prepare__(metacls, name, bases):
        """Prepare the class dict to be an `OrderedDict`.

        Parameters
        ----------
        name : str
            Name of the class, or meta class instance.
        bases : tuple of type
            Bases of the class, or meta class instance.

        """
        return PublicOrderedDict()

    def __new__(cls, classname, bases, class_dict):
        """Instantiate a meta class, resulting in a class.

        Parameters
        ----------
        classname : str
            Name of the class, or meta class instance.
        bases : tuple of type
            Bases of the class, or meta class instance.
        class_dict : :obj:`InstanceTracker`
            The class' to-be __dict__. In this case, with the addition of tracker attributes.

        """
        result = super().__new__(cls, classname, bases, dict(class_dict))
        try:
            tracked = result.__tracked__
        except AttributeError:
            # if there is no attribute `__tracked__`, we do not inherit it
            tracked = class_dict.public()
        else:
            # otherwise we inherit from another base, copy tracked dict and append our new one
            tracked = result.__tracked__.copy()
            tracked.update(class_dict.public())
        result.__tracked__ = tracked
        return result


class Tracker(metaclass=MetaTracker):
    @classmethod
    def collect(cls, dtype):
        return OrderedDict((key, val) for key, val in cls.__tracked__.items() if isinstance(val, dtype))

    def collect_attr(self, dtype):
        return OrderedDict((key, getattr(self, key)) for key, val in self.__tracked__.items() if isinstance(val, dtype))
