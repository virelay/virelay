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
