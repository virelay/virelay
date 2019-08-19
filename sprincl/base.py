"""Module containing basic Sprincl classes, such as Param"""
from .plugboard import Slot


class Param(Slot):
    """A single parameter, which instances are to be tracked by a `MetaTracker`.

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
        super().__init__(dtype, default)
        if mandatory:
            del self.default

        # allowed_dtypes = (type, FunctionType, BuiltinFunctionType)
        # if not all(isinstance(x, allowed_dtypes) for x in self.dtype):
        #     raise TypeError(
        #         "Following dtypes: {} are not in the allowed types {}.".format(self.dtype, allowed_dtypes)
        #     )
