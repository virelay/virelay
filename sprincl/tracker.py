"""Includes MetaTracker to track definition order of class attributes.

"""
from collections import OrderedDict


class InstanceTracker(dict):
    """Track items of instances of specified type(s) in a seperate OrderedDict.

    Tracked items will not be added to __dict__.

    Attributes
    ----------
    tracked : :obj:`collections.OrderedDict`
        Stores tracked attributes in order.

    """
    def __init__(self, attr_class, attr_name):
        """Configure instance tracker.

        Parameters
        ----------
        attr_class : type or tuple of type
            Type or types of attribute instances to be tracked.
        attr_name : str
            The attribute name as which the `OrderedDict` of tracked items shold be registered in the `MetaTracker`.
            Attributes in `InstanceTracker` are always stored in the in attribute `tracked`.

        """
        self.tracked = OrderedDict()
        self.attr_class = attr_class
        self.attr_name = attr_name

    def __setitem__(self, key, value):
        """Assigned items are checked whether they are an instance of self.attr_class, and if they are, added to
        `self.tracked`. Otherwise, items are put into the class_dict.

        Parameters
        ----------
        key : str
            Name of the attribute.
        value : object
            Value of the attribute

        """
        if key not in self.tracked and isinstance(value, self.attr_class):
            self.tracked[key] = value
        else:
            dict.__setitem__(self, key, value)


class MetaTracker(type):
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
    def sub(metacls, class_name, attr_class, attr_name):
        """Convenience method to dynamically create a sub meta class where attributes `attr_class` and `attr_name` are
        assigned meta class attributes. This is needed so the tracker can be properly configured in
        `MetaTracker.__prepare__`.

        Parameters
        ----------
        attr_class : type or tuple of type
            Type or types of attribute instances to be tracked by `InstanceTracker`.
        attr_name : str
            The attribute name as which the `OrderedDict` of tracked items shold be registered in the `MetaTracker`.
            Attributes in `InstanceTracker` are always stored in the in attribute `tracked`.

        Returns
        -------
        type
            Sub meta class of `MetaTracker` with attributes `attr_class` and `attr_name` set, ready for use in a class
            definition.

        """
        return type(class_name, (metacls,), dict(attr_class=attr_class, attr_name=attr_name))

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
        return InstanceTracker(metacls.attr_class, metacls.attr_name)

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
        # strip frills from InstanceTracker
        stripped_class_dict = dict(class_dict)
        result = type.__new__(cls, classname, bases, stripped_class_dict)
        if hasattr(result, class_dict.attr_name):
            # if we inherit task_scheme from another base, copy it and append our new scheme
            setattr(result, class_dict.attr_name, getattr(result, class_dict.attr_name).copy())
            getattr(result, class_dict.attr_name).update(class_dict.tracked)
        else:
            # otherwise just use our new scheme
            setattr(result, class_dict.attr_name, class_dict.tracked)
        return result
