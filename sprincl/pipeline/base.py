"""Base classes Task and Pipeline.

"""
from collections import OrderedDict

from ..tracker import MetaTracker
from ..processor.base import ensure_processor, Processor


class Task:
    """A single item in a :obj:`Pipeline` task scheme.

    Attributes
    ----------
    proc_type : type
        Class of the :obj:`Processor`s allowed for this :obj:`Task`.
    default : :obj:`Processor` or :obj:`types.FunctionType` or :obj:`types.MethodType` Default :obj:`Processor` to use
        if no Processor is assigned. If a :obj:`types.FunctionType` or :obj:`types.MethodType`, an appropriate
        :obj:`FunctionProcessor` will be created.
    proc_kwargs : dict
        Keyword arguments to overwrite on the supplied Processor.

    """
    def __init__(self, proc_type=Processor, default=(lambda data: data), **kwargs):
        """Configure :obj:`Task` instance.

        Parameters
        ----------
        proc_type : type
            Class of the :obj:`Processor`s allowed for this :obj:`Task`.
        default : :obj:`Processor` or :obj:`types.FunctionType` or :obj:`types.MethodType` Default :obj:`Processor` to
            use if no Processor is assigned. If a :obj:`types.FunctionType` or :obj:`types.MethodType`, an appropriate
            :obj:`FunctionProcessor` will be created.
        **kwargs :
            Keyword arguments to overwrite on the supplied Processor.

        Raises
        ------
        TypeError
            If the default :obj:`Processor` is not of type `proc_type`.

        """
        default = ensure_processor(default, **kwargs)
        if not isinstance(default, proc_type):
            raise TypeError('Task default processor {} is not of type {}!'.format(default, proc_type))
        self.proc_type = proc_type
        self.default = default
        self.proc_kwargs = kwargs


class Pipeline(metaclass=MetaTracker.sub('MetaPipeline', Task, 'task_scheme')):
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
            proc = ensure_processor(kwargs.get(key, task.default.copy()), **task.proc_kwargs)
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
            Output of all :obj:`Processor`s in `self.processes` that are flagged as pipeline outputs. If no processors
            are flagged as outputs, return the output of the last processor.

        """
        outputs = []
        for proc in self.processes.values():
            data = proc(data)
            if proc.is_output:
                outputs.append(data)
        if not outputs:
            return data
        if len(outputs) == 1:
            return outputs[0]
        return tuple(outputs)

    def __repr__(self):
        """Example of the pipeline representation:
        MyPipeline(
            FunctionProcessor(function=(lambda x: x.mean(1)),) -> output:np.ndarray
            SciPyPDist(metric=sqeuclidean) -> output:np.ndarray
            RadialBasisFunction(sigma=0.1) -> output:np.ndarray
            MyProcess(stuff=3, func=Param(FunctionType, lambda x: x**2)) -> output:np.ndarray
        )
        """
        pipeline = '\n    '.join([proc.__repr__() for proc in self.processes.values()])
        return '{}(\n    {}\n)'.format(self.__class__.__name__, pipeline)
