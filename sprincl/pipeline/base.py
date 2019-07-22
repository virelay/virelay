"""Base classes Task and Pipeline.

"""
from collections import OrderedDict

from ..tracker import MetaTracker
from ..processor.base import ensure_processor


class Task(object):
    """A single item in a Pipeline Task Scheme

    """
    def __init__(self, proc_type=object, default=(lambda x: x), is_output=False):
        default = ensure_processor(default)
        if not isinstance(default, proc_type):
            raise TypeError('Task default processor {} is not of type {}!'.format(default, proc_type))
        self.proc_type = proc_type
        self.default = default
        self.is_output = is_output


class Pipeline(object, metaclass=MetaTracker.sub('MetaPipeline', Task, 'task_scheme')):
    """Abstract base class for all pipelines using MetaPipeline's tracked Task attributes

    """
    def __init__(self, *args, **kwargs):
        self.processes = OrderedDict()
        for key, task in self.task_scheme.items():
            proc = ensure_processor(kwargs.get(key, task.default.copy()), is_output=task.is_output)
            if not isinstance(proc, task.proc_type):
                raise TypeError('Task {} function {} is not of type {}!'.format(key, proc.func, task.proc_type))
            self.processes[key] = proc

    def checkpoint_processes(self):
        checkpoint_process_list = []
        for key, proc in reversed(self.processes.items()):
            checkpoint_process_list.append((key, proc))
            if proc.is_checkpoint:
                break
        if not proc.is_checkpoint:
            raise RuntimeError("No checkpoint defined!")
        checkpoint_processes = OrderedDict(checkpoint_process_list[::-1])
        return checkpoint_processes

    def from_checkpoint(self):
        """Re-evaluate from last checkpoint

        """
        checkpoint_processes = self.checkpoint_processes()
        data = next(iter(checkpoint_processes.values())).checkpoint_data
        if data is None:
            raise RuntimeError("No checkpoint data! Run whole pipeline first!")
        for proc in checkpoint_processes.values():
            data = proc(data)
        return data

    def __call__(self, data):
        for proc in self.processes.values():
            data = proc(data)
        return data
