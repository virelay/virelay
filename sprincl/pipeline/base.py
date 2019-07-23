"""Base classes Task and Pipeline.

"""
from collections import OrderedDict

from ..tracker import MetaTracker
from ..processor.base import ensure_processor


class Task(object):
    """A single item in a :obj:`Pipeline` task scheme.

    Attributes
    ----------
    proc_type : type
        Class of the :obj:`Processor`s allowed for this :obj:`Task`.
    default : :obj:`Processor` or callable
        Default :obj:`Processor` to use if no Processor is assigned. If callable, an appropriate
        :obj:`FunctionProcessor` will be created.
    is_output : bool
        Whether :obj:`Processor`s assigned to this Task should yield an output for the :obj:`Pipeline`.

    """
    def __init__(self, proc_type=object, default=(lambda x: x), is_output=False):
        """Configure :obj:`Task` instance.

        Parameters
        ----------
        proc_type : type
            Class of the :obj:`Processor`s allowed for this :obj:`Task`.
        default : :obj:`Processor` or callable
            Default :obj:`Processor` to use if no Processor is assigned. If callable, an appropriate
            :obj:`FunctionProcessor` will be created.
        is_output : bool
            Whether :obj:`Processor`s assigned to this Task should yield an output for the :obj:`Pipeline`.

        Raises
        ------
        TypeError
            If the default :obj:`Processor` is not of type `proc_type`.

        """
        default = ensure_processor(default)
        if not isinstance(default, proc_type):
            raise TypeError('Task default processor {} is not of type {}!'.format(default, proc_type))
        self.proc_type = proc_type
        self.default = default
        self.is_output = is_output


class Pipeline(object, metaclass=MetaTracker.sub('MetaPipeline', Task, 'task_scheme')):
    """Abstract base class for all pipelines using MetaPipeline's tracked Task attributes

    Attributes
    ----------
    task_scheme : :obj:`collections.OrderedDict`
        OrderedDict of Tasks which can be filled with :obj:`Processor`s.
    processes : :obj:`collections.OrderedDict`
        OrderedDict of the :obj:`Processor`s that filled the `task_scheme`.

    """
    def __init__(self, **kwargs):
        """Configure :obj:`Pipeline` instance

        Parameters
        ----------
        **kwargs :
            Keyword arguments with keys named identical to the pipeline tasks, and values of type :obj:`Processor` to
            fill these :obj:`Task`s.

        Raises
        ------
        TypeError
            If some :obj:`Processor` does not have a matching type of the :obj:`Task` it has be assigned to.

        """
        self.processes = OrderedDict()
        for key, task in self.task_scheme.items():
            proc = ensure_processor(kwargs.get(key, task.default.copy()), is_output=task.is_output)
            if not isinstance(proc, task.proc_type):
                raise TypeError('Task {} function {} is not of type {}!'.format(key, proc.func, task.proc_type))
            self.processes[key] = proc

    def checkpoint_processes(self):
        """Find the checkpoint :obj:`Processor` closest to output in `self.processes` and return an
        :obj:`collections.OrderedDict` of that and all following :obj:`Processor`s in `self.processes`.

        Returns
        -------
        :obj:`collections.OrderedDict`
            The :obj:`Processor` that is the checkpoint closest to output in `self.processes` and all its following
            :obj:`Processor`s in an :obj:`OrderedDict`.

        Raises
        ------
        RuntimeError
            If there is not a single checkpoint in `self.processes`

        """
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
        """Re-evaluate from last checkpointed :obj:`Processor` using its respective output.

        Returns
        -------
        object
            Output of the whole pipeline, starting from checkpointed :obj:`Processor` closest to output in
            `self.processes`.

        Raises
        ------
        RuntimeError
            If the checkpointed :obj:`Processor` closest to output in `self.processes` does not have any
            `checkpoint_data` store, i.e. the :obj:`Processor` was never called once after being declared a checkpoint.

        """
        checkpoint_processes = self.checkpoint_processes()
        data_iter = iter(checkpoint_processes.values())
        data = next(data_iter).checkpoint_data
        if data is None:
            raise RuntimeError("No checkpoint data! Run whole pipeline first!")
        for proc in data_iter:
            data = proc(data)
        return data

    def __call__(self, data):
        """Propagate `data` through the whole pipeline from front to back, calling all `self.processes` in series.

        Attributes
        ----------
        data :
            The pipeline input passed to the first :obj:`Processor` in `self.processors`. Type depends on first
            :obj:`Processor`.

        Returns
        -------
        object
            Output of all :obj:`Processor`s in `self.processes` that are flagged as pipelin outputs.

        """
        for proc in self.processes.values():
            data = proc(data)
        return data
