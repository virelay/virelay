"""Sprincl utils contains conditional importing functionality.

"""

from importlib import import_module


def dummy_from_module_import(name):
    """Use to replace 'from lib import func'."""
    def func(*args, **kwargs):
        raise RuntimeError("Support for {1} was not installed! Install with: pip install {0}[{1}]".format(
            __name__.split('.')[0], name
        ))
    return func


def dummy_import_module(name):
    """Use to replace 'import lib`."""
    class Class:
        """Dummy substitute class."""
        def __getattr__(self, item):
            raise RuntimeError("Support for {1} was not installed! Install with: pip install {0}[{1}]".format(
                __name__.split('.')[0], name))

    return Class()


def import_or_stub(name, subname=None):
    """Use to conditionally import packages.

    Parameters
    ----------
    name: str
        Module name. Ie. 'module.lib'
    subname: tuple[str] or str or None
        Functions or classes to be imported from 'name'.
    """
    subnames = (subname, ) if isinstance(subname, str) else subname  # convert to tuple
    if subname is not None:
        try:
            tmp = import_module(name)
        except ImportError:
            module = [dummy_from_module_import(name) for _ in subnames]
        else:
            module = []
            for subname in subnames:
                try:
                    attr = getattr(tmp, subname)
                except AttributeError as err:
                    message = "cannot import name '{}' from '{}' ({})".format(subname, name, tmp.__file__)
                    raise ImportError(message) from err
                else:
                    module.append(attr)
        if len(module) == 1:
            module = module[0]
    else:
        try:
            module = import_module(name)
        except ImportError:
            module = dummy_import_module(name)
    return module
