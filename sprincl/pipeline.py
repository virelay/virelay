from collections import OrderedDict

class Task(object):
    """A single item in a Pipeline Task Scheme

    """
    def __init__(self, ttype=object, default=(lambda x: x)):
        if not isinstance(default, ttype):
            raise TypeError('Task default function {} is not of type {}!'.format(default, ttype))
        self.ttype = ttype
        self.default = default

class TaskOrder(dict):
    """Track Task items in a seperate OrderedDict

    """
    def __init__(self):
        self.task_scheme = OrderedDict()

    def __setitem__(self, key, value):
        if key not in self.task_scheme and isinstance(value, Task):
            self.task_scheme[key] = value

        dict.__setitem__(self, key, value)

class MetaPipeline(type):
    """MetaClass for Pipelines to track attributes of type Task in order of declaration

        Note
        ----
        See PEP3115
    """
    @classmethod
    def __prepare__(metacls, name, bases):
        return TaskOrder()

    def __new__(cls, classname, bases, classdict):
        result = type.__new__(cls, classname, bases, dict(classdict))
        if hasattr(result, 'task_scheme'):
            # if we inherit task_scheme from another base, copy it and append our new scheme
            result.task_scheme = result.task_scheme.copy()
            result.task_scheme.update(classdict.task_scheme)
        else:
            # otherwise just use our new scheme
            result.task_scheme = classdict.task_scheme
        return result

class Pipeline(object, metaclass=MetaPipeline):
    """Abstract base class for all pipelines using MetaPipeline's tracked Task attributes

    """
    def __init__(self, *args, **kwargs):
        self.tasks = OrderedDict()
        for key, task in self.task_scheme.items():
            func = kwargs.get(key, task.default)
            if not isinstance(func, task.ttype):
                raise TypeError('Task {} function {} is not of type {}!'.format(key, func, task.ttype))
            if not callable(func):
                raise RuntimeError('Task {} function {} is not callable!'.format(key, func))
            self.tasks[key] = func

    def __call__(self, data):
        for key, task in self.tasks.items():
            data = task(data)
        return data

