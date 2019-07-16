from collections import OrderedDict

class InstanceTracker(dict):
    """Track items of instances of specified type(s) in a seperate OrderedDict

    """
    def __init__(self, attr_class, attr_name):
        self.tracked = OrderedDict()
        self.attr_class = attr_class
        self.attr_name = attr_name

    def __setitem__(self, key, value):
        # register items either in tracked, or in class_dict
        if key not in self.tracked and isinstance(value, self.attr_class):
            self.tracked[key] = value
        else:
            dict.__setitem__(self, key, value)

class MetaTracker(type):
    """Meta class to track attributes of some type in order of declaration

    Needs to be sub-classed with attributes 'attr_class' and 'attr_name' set. Classmethod 'sub' can be used for this.
    AFAIK, there is no better way to pass inherited parameters to class creation.
    Passing keywords to class creation is not retained in inherited classes.

    Note
    ----
    See PEP3115

    """
    @classmethod
    def sub(metacls, class_name, attr_class, attr_name):
        return type(class_name, (metacls,), dict(attr_class=attr_class, attr_name=attr_name))

    @classmethod
    def __prepare__(metacls, name, bases):
        return InstanceTracker(metacls.attr_class, metacls.attr_name)

    def __new__(cls, classname, bases, class_dict):
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

