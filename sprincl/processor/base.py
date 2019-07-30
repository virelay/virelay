"""Base classes Param and Processor.

"""
import inspect
from types import FunctionType, MethodType, LambdaType

from sprincl.io import DataStorageBase, HDF5Storage
from ..tracker import MetaTracker


class Param(object):
    """A single parameter, which instances are to be tracked by an `MetaTracker`.

    Attributes
    ----------
    dtype : type or tuple of type
        Allowed type(s) of the parameter.
    default : :obj:`dtype`
        Default parameter value, should be an instance of (one of) :obj:`dtype`.

    """
    def __init__(self, dtype, default=None, mandatory=False):
        """Configure type and default value of parameter.

        Parameters
        ----------
        dtype : type or tuple of type
            Allowed type(s) of the parameter.
        default : :obj:`dtype`
            Default parameter value, should be an instance of (one of) :obj:`dtype`.

        """
        self.dtype = dtype if isinstance(dtype, tuple) else (dtype,)
        self.default = default
        self.mandatory = mandatory

        if not all(isinstance(dty, type) for dty in self.dtype):
            raise TypeError("Only instances of type are a valid dtype!")
        if default is not None and not isinstance(default, dtype):
            raise TypeError("Default object is not of supplied dtype!")


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
    is_output = Param(bool, False)
    is_checkpoint = Param(bool, False)
    io = Param(DataStorageBase, None)
    storage_key = Param(str, 'data')

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
        self.reset_defaults()
        for key, param in self.params.items():
            if param.mandatory and key not in kwargs:
                raise TypeError('{} parameter {} is mandatory.'.format(key, param.dtype))
            try:
                attr = kwargs.pop(key)
            except KeyError:
                continue
            if attr is not None and not isinstance(attr, param.dtype):
                raise TypeError('{} parameter is no subtype of {}.'.format(key, param.dtype))
            setattr(self, key, attr)
        if kwargs:
            key, _ = kwargs.popitem()
            raise TypeError('\'{}\' is an invalid keyword argument'.format(key))
        self.checkpoint_data = None

    def __getattr__(self, name):
        """Return default param values if attribute is not set.

        """
        try:
            return self._default_param_values[name]
        except KeyError:
            pass
        raise AttributeError('\'{} \' has no attribute \'{}\''.format(type(self), name))

    def reset_defaults(self):
        """Reset dictionary for the default (fallback) values of parameters to their parameter defaults.

        """
        self._default_param_values = {key: param.default for key, param in self.params.items()}

    def update_defaults(self, **kwargs):
        """Update dictionary for the default (fallback) values of parameters!

        Parameters that are not explicitly assigned as an instance attribute are retrieved from the default dict.

        Parameters
        ----------
        **kwargs :
            Names of Params to be updated. Only existing Params are allowed.

        Raises
        ------
        KeyError
            If a keyword argument is supplied that does not describe any existing Param.

        """
        for key, val in kwargs.items():
            if key in self._default_param_values:
                if not isinstance(val, self.params[key].dtype):
                    raise TypeError('{} parameter is no subtype of {}.'.format(key, self.params[key].dtype))
                self._default_param_values[key] = val
            else:
                raise KeyError('Name \'{}\' does not describe any existing Param!'.format(key))

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
        if self.io is not None:
            self.write(self.storage_key, out)
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

    def write(self, key, data):
        if self.io is None:
            raise AttributeError('io not defined.')
        #self.io['param_values'] = self.param_values()
        self.io[key] = data

    def _output_repr(self):
        return 'output:np.ndarray'

    def __repr__(self):
        """Return Processor's representation.
        I.e.: ProcessorName(metric=sqeuclidean, function=lambda x: x.mean(1)) -> output: np.ndarray
        Replace self._output_repr for output representation. Default: output:np.ndarray.

        """

        def transform(x):
            """If x is a lambda function, return the source.

            """
            if isinstance(x, LambdaType):
                return inspect.getsource(x).split('=', 1)[1].strip()
            else:
                return x

        name = self.__class__.__name__
        params = ', '.join(['{}={}'.format(k, transform(v)) for k, v in self.param_values().items() if v])
        return '{}({}) -> {}'.format(name, params, self._output_repr())

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
    function : :obj:`types.FunctionType` or :obj:`types.MethodType`
        The function around which to create the :obj:`FunctionProcessor`. It wil be bound as a method if bind_method.
    bind_method : bool
        Will bind `function` to this class, enabling it to access `self`.

    """
    function = Param((MethodType, FunctionType), (lambda self, data: data))
    bind_method = Param(bool, False)

    def __init__(self, **kwargs):
        """Bind function as attribute of instance.

        See also
        --------
        :obj:`Processor`

        """
        super().__init__(**kwargs)
        if self.bind_method:
            self.function = self.function.__get__(self, type(self))


def ensure_processor(proc, **kwargs):
    """Make sure argument is a Processor and, if it is not, but callable, make it a FunctionProcessor. Set attributes of
    resulting processor as stated in `**kwargs`.

    Parameters
    ----------
    proc : Processor or callable
        Object to ensure to be a :obj:`Processor`.
    **kwargs :
        Keyword arguments stating new default values for Parameters of `proc`.

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
    proc.update_defaults(**kwargs)
    return proc
