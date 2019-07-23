"""Base classes Param and Processor.

"""
from ..tracker import MetaTracker


class Param(object):
    """A single parameter, which instances are to be tracked by an `MetaTracker`.


    Attributes
    ----------
    dtype : type
        Type of the parameter.
    default : :obj:`dtype`
        Default parameter value, should be an instance of :obj:`dtype`.

    """
    def __init__(self, dtype, default=None):
        """Configure type and default value of parameter.

        Parameters
        ----------
        dtype : type
            Type of the parameter.
        default : :obj:`dtype`
            Default parameter value, should be an instance of :obj:`dtype`.

        """
        self.dtype = dtype
        self.default = default


class Processor(object, metaclass=MetaTracker.sub('MetaProcessor', Param, 'params')):
    """Base class of processors of tasks in a pipeline instance.

    Attributes of type :obj:`Param` are tracked as the class' attribute `params` of type :obj:`collections.OrderedDict`.
    All tracked attributes will be assigned as instance attributes in `__init__`.

    Attributes
    ----------
    params : :obj:`collections.OrderedDict`
        OrderedDict of all assigned class attributes of type :obj:`Param`.
    is_output : bool
        Assigned as :obj:`Param`, will be assigned as an instance attribute in `__init__`.
        Defines whether the Processor should yield an output for a Pipeline.
    is_checkpoint : bool
        Assigned as :obj:`Param`, will be assigned as an instance attribute in `__init__`.
        Defines whether checkpointed pipeline computations should start at this point, if there exists a previously
        computed checkpoint value.
    checkpoint_data : object
        If this Processor is a checkpoint, and if the Processor was called at least once, stores the output of this
        processor.

    """
    is_output = Param(bool, None)
    is_checkpoint = Param(bool, False)

    def __init__(self, **kwargs):
        """Initialize all :obj:`Param` defined parameters to either there default value or, if supplied as keyword
        argument, to the value supplied.

        Parameters
        ----------
        is_checkpoint : bool
            Whether the Processor should yield an output for a Pipeline.
        is_output : bool
            Whether checkpointed pipeline computations should start at this point, if there exists a previously computed
            checkpoint value.
        **kwargs : dict
            Other potential parameters defined in sub classes.

        """
        for key, param in self.params.items():
            setattr(self, key, kwargs.get(key, param.default))
        self.checkpoint_data = None

    def function(self, data):
        """Abstract function this Processor should apply on input

        Parameters
        ----------
        data : object
            Input data to this Processor.

        Raises
        ------
        NotImplementedError
            Always, since this is an abstract function.
        """
        raise NotImplementedError

    def __call__(self, data):
        """Apply `self.funtion` on input data, save output if `self.is_checkpoint`

        Parameters
        ----------
        data : object
            Input data to this Processor.

        Returns
        -------
        object
            Depending on what operation `self.function` executes.

        """
        out = self.function(data)
        if self.is_checkpoint:
            self.checkpoint_data = out
        return out

    def param_values(self):
        """Get values for all parameters defined through :obj:`Param` attributes.

        Returns
        -------
        dict of object
            Dict of the instance values of defined parameters.

        """
        return {key: getattr(self, key) for key in self.params}

    def copy(self):
        """Copy self, creating a new Processor instance with the same values for :obj:`Param` attribute defined
        parameters.

        Returns
        -------
        :obj:`Processor`
            New instance with copied parameter values.

        """
        new = type(self)(**self.param_values())
        new.checkpoint_data = self.checkpoint_data
        return new

    # TODO: this is not yet clean chaining, we have to find the common base, which is something like the second-to-top
    # class
    # def __add__(self, other):
    #     common_base = type(self)
    #     if not isinstance(other, common_base)
    #         raise TypeError("Processor-chaining: expected instance of type '{}', got '{}'."
    #                         .format(common_base, type(other))
    #                     )
    #     if not isinstance(self, ChainedProcessor):
    #         chained_proc = type("Chained{}".format(common_base),
    #                            [common_base, ChainedProcessor], {})(chain=[self, other], **self.param_values())
    #     else:
    #         chain = self.chain + [other]
    #         chained_proc = type(self)(**self.param_values())
    #     return chained_proc


# TODO: Chained Processors
# class ChainedProcessor(Processor):
#     chain = Param(list, [])
#
#     def function(self, data):
#         for proc in self.chain:
#             data = proc(data)
#         return data


class FunctionProcessor(Processor):
    """Processor instance initialized with a supplied function

    Attributes
    ----------
    function : callable
        The function around which to create the :obj:`FunctionProcessor`.

    """
    function = Param(callable, (lambda self, data: data))


def ensure_processor(proc, **kwargs):
    """Make sure argument is a Processor and, if it is not, but callable, make it a FunctionProcessor. Set attributes of
    resulting processor as stated in `**kwargs`.

    Parameters
    ----------
    proc : Processor or callable
        Object to ensure to be a :obj:`Processor`.
    **kwargs :
        Keyword arguments stating attributes of `proc` to change.

    Returns
    -------
    :obj:`Processor`
        Original object `proc` with updated attributes if it was a Processor, else a :obj:`FunctionProcessor` with
        supplied function.
        `proc` and attributes as given in `**kwargs`.

    """
    if not isinstance(proc, Processor):
        if callable(proc):
            proc = FunctionProcessor(function=proc)
        else:
            raise TypeError('Supplied processor {} is neither a Processor, nor callable!')
    for key, val in kwargs.items():
        if getattr(proc, key, None) is None:
            setattr(proc, key, val)
    return proc
