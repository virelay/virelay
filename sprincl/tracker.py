"""Includes MetaTracker to track definition order of class attributes."""
from collections import OrderedDict
from abc import ABCMeta


class MetaTracker(ABCMeta):
    """Meta class to track attributes of some type in order of declaration

    Needs to be sub-classed with attributes 'attr_class' and 'attr_name' set. Classmethod 'sub' can be used for this.

    Tracked attributes can be overwritten for instances by supplying the attribute's name as a keyword argument for
    `MetaTracker.__init__`.


    Example
    -------
    >>> class OrderedInts(metaclass=MetaTracker.sub('IntMetaTracker', int, 'ints')):
    ...     a = 14
    ...     b = 21
    ...     c = 42
    ... OrderedInts(a=0).ints
    OrderedDict([('a', 0), ('b', 21), ('c', 42)])

    Note
    ----
    There does not seem to be a better way to pass inherited parameters to class creation. Passing keywords to class
    creation is not retained in inherited classes.

    See PEP3115

    """
    @classmethod
    def __prepare__(metacls, name, bases):
        """Prepare the class dict to be an `InstanceTracker`. We store `attr_name` using the `InstanceTracker` as we
        later do not have any other means to restore the attribute. The class does not exist yet.

        Parameters
        ----------
        name : str
            Name of the class, or meta class instance.
        bases : tuple of type
            Bases of the class, or meta class instance.

        """
        return OrderedDict()

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
        if hasattr(result, class_dict.attr_name):
            # if we inherit from another base, copy tracked dict and append our new one
            result.__tracked__ = result.__tracked__.copy()
            result.__tracked__.update(class_dict)
        else:
            # otherwise just use our new tracked dict
            result.__tracked__ = class_dict
        return result


class Tracker(metaclass=MetaTracker):
    @classmethod
    def collect(cls, dtype):
        return OrderedDict((key, val) for key, val in cls.__tracked__ if isinstance(val, dtype))
