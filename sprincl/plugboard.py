"""Plugboards are classes which contain Slots that are filled using Plugs."""
from .tracker import Tracker


class EmptyInit(object):
    def __init__(self):
        super().__init__()


class Slot(EmptyInit):
    """

    Attributes
    ----------
    dtype : type or tuple of type
        Allowed type(s) of the parameter.
    default : :obj:`dtype`
        Default parameter value, should be an instance of (one of) :obj:`dtype`.

    """
    def __init__(self, dtype=object, default=None, **kwargs):
        """Configure type and default value of slot.

        Parameters
        ----------
        dtype : type or tuple of type
            Allowed type(s) inside the slot.
        default : :obj:`dtype`
            Default plug value, should be an instance of (one of) :obj:`dtype`.

        """
        super().__init__(**kwargs)
        self._dtype = dtype if isinstance(dtype, tuple) else (dtype,)
        self._default = default
        self.__name__ = ''
        self._consistent()

    def _consistent(self):
        if (
            not isinstance(self.dtype, type)
            and not (
                isinstance(self.dtype, tuple)
                and all(isinstance(element, type) for element in self.dtype)
            )
        ):
            raise TypeError(
                "'{}' object '{}' default values '{}' is neither a type, nor a tuple of types.".format(
                    type(self).__name__,
                    self.__name__,
                    self.dtype
                )
            )
        if self.default is not None and not isinstance(self.default, self.dtype):
            raise TypeError(
                "'{}' object '{}' default value is not of type '{}'.".format(
                    type(self).__name__,
                    self.__name__,
                    self.dtype
                )
            )

    def get_plug(self, instance, obj=None, default=None):
        try:
            plug = instance.__dict__[self.__name__]
        except KeyError:
            plug = self(obj=obj, default=default)
            instance.__dict__[self.__name__] = plug
        return plug

    def __set_name__(self, owner, name):
        self.__name__ = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.get_plug(instance).obj

    def __set__(self, instance, value):
        self.get_plug(instance, obj=value).obj = value

    def __delete__(self, instance):
        del self.get_plug(instance).obj

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        self._default = value
        self._consistent()

    @default.deleter
    def default(self):
        self._default = None

    @property
    def dtype(self):
        return self._dtype

    @dtype.setter
    def dtype(self, value):
        self._dtype = value
        self._consistent()

    @property
    def optional(self):
        return self.default is not None

    def __call__(self, obj=None, default=None):
        return Plug(self, obj=obj, default=default)


class Plug(EmptyInit):
    def __init__(self, slot, obj=None, default=None, **kwargs):
        super().__init__(**kwargs)
        self._obj = obj
        self._slot = slot
        self._default = default
        self._consistent()

    def _consistent(self):
        if self.obj is None:
            raise TypeError(
                "'{}' object '{}' is mandatory, yet it has been accessed without being set.".format(
                    type(self.slot).__name__,
                    self.slot.__name__
                )
            )
        if not isinstance(self.obj, self.slot.dtype):
            raise TypeError(
                "'{}' object '{}' value '{}' is not of type '{}'.".format(
                    type(self.slot).__name__,
                    self.slot.__name__,
                    self.obj,
                    self.slot.dtype
                )
            )

    @property
    def slot(self):
        return self._slot

    @slot.setter
    def slot(self, value):
        self._slot = value
        self._consistent()

    @property
    def dtype(self):
        return self.slot.dtype

    @property
    def optional(self):
        return self.default is not None

    @property
    def fallback(self):
        return self.slot.default

    @property
    def obj(self):
        if self._obj is None:
            return self.default
        return self._obj

    @obj.setter
    def obj(self, value):
        self._obj = value
        self._consistent()

    @obj.deleter
    def obj(self):
        self.obj = None

    @property
    def default(self):
        if self._default is None:
            return self.fallback
        return self._default

    @default.setter
    def default(self, value):
        self._default = value
        self._consistent()

    @default.deleter
    def default(self):
        self.default = None


class SlotDefaultAccess:
    def __init__(self, instance=None):
        object.__setattr__(self, '_instance', instance)

    def _get_plug(self, name, default=None):
        slot = getattr(type(self._instance), name)
        if not isinstance(slot, Slot):
            raise AttributeError(
                "'{}' object has no attribute '{}' of type '{}'".format(
                    type(self._instance),
                    name,
                    Slot
                )
            )
        return slot.get_plug(self._instance, default=default)

    def __get__(self, instance, owner):
        return type(self)(instance)

    def __set__(self, instance, value):
        self = type(self)(instance)
        if not isinstance(value, dict):
            raise TypeError("Can only directly set default values using a dict!")
        for key, val in value.items():
            setattr(self, key, val)

    def __getattr__(self, name):
        return self._get_plug(name).default

    def __setattr__(self, name, value):
        self._get_plug(name, default=value).default = value

    def __delattr__(self, name):
        del self._get_plug(name).default

    def __dir__(self):
        return list(type(self._instance).collect(Slot))


class Plugboard(Tracker, EmptyInit):
    default = SlotDefaultAccess()

    def __init__(self, **kwargs):
        slots = self.collect(Slot)
        non_slot_kwargs = {key: val for key, val in kwargs.items() if key not in slots}
        # also pass responsibility to raise Exception on wrong kwargs to super-class
        super().__init__(**non_slot_kwargs)
        for key, val in kwargs.items():
            setattr(self, key, val)

    def reset_defaults(self):
        for key in self.collect(Slot):
            delattr(self.default, key)

    def update_defaults(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self.default, key, val)
