from ..tracker import Tracker


class Slot(object):
    def __init__(self, dtype=object, default=None):
        self._dtype = dtype
        self._default = default
        if not isinstance(default, dtype):
            raise TypeError

    def get_plug(self, instance, default=None):
        try:
            plug = instance.__dict__[self.__name__]
        except KeyError:
            plug = self(default)
            instance.__dict__[self.__name__] = plug
        return plug

    def __set_name__(self, owner, name):
        self.__name__ = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.get_plug(instance).obj

    def __set__(self, instance, value):
        self.get_plug(instance, value).obj = value

    def __delete__(self, instance):
        del self.get_plug(instance).obj

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value):
        if not isinstance(value, self.dtype):
            raise TypeError
        self._default = value

    @property
    def dtype(self):
        return self._dtype

    @dtype.setter
    def dtype(self, value):
        if not isinstance(self.default, value):
            raise TypeError
        self._dtype = value

    @property
    def optional(self):
        return self.default is not None

    def __call__(self, obj=None):
        return Plug(obj, self)


class Plug(object):
    def __init__(self, obj, slot):
        self._obj = obj
        self._slot = slot
        self._default = slot.default
        if not isinstance(obj, slot.dtype):
            raise TypeError
        if not slot.optional and obj is None:
            raise TypeError

    @property
    def slot(self):
        return self._slot

    @slot.setter
    def slot(self, value):
        if not isinstance(self.obj, value.dtype):
            raise TypeError
        if not value.optional and self.obj is None:
            raise TypeError
        self._slot = value

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
        if not isinstance(value, self.dtype):
            raise TypeError
        if not self.optional and value is None:
            raise TypeError
        self._obj = value

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
        if not isinstance(value, self.dtype):
            raise TypeError
        self._default = value

    @default.deleter
    def default(self, value):
        self.default = None


class SlotDefaultAccess:
    def __init__(self, instance=None):
        self._instance = instance

    def _get_plug(self, name):
        slot = getattr(type(self._instance), name)
        if not isinstance(slot, Slot):
            raise AttributeError(
                "'{}' object has no attribute '{}' of type '{}'".format(
                    type(self._instance),
                    name,
                    Slot
                )
            )
        return slot.get_plug(self._instance)

    def __get__(self, instance, owner):
        return type(self)(instance)

    def __set__(self, instance, value):
        if not isinstance(value, dict):
            raise TypeError
        for key, val in value:
            getattr(self, key).default

    def __getattr__(self, name):
        return self._get_plug(name).default

    def __setattr__(self, name, value):
        self._get_plug(name).default = value

    def __delattr__(self, name):
        del self._get_plug(name).default

    def __dir__(self):
        return list(type(self._instance).collect(Slot))


class Plugboard(Tracker):
    default = SlotDefaultAccess()

    def __init__(self, **kwargs):
        slots = self.collect(Slot)
        for key, val in kwargs:
            if key not in slots:
                raise TypeError(
                    "invalid keyword argument '{}' for '{}' object: no such attribute of type '{}'".format(
                        key,
                        type(self),
                        Slot
                    )
                )
            setattr(self, key, val)
