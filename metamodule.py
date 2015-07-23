# This is metamodule.py.
# Copyright (C) 2014-2015 Nathaniel J. Smith <njs@pobox.com>
# Released under a 2-clause BSD license; see the LICENSE file for details.

"A tiny Python module for taking control of your library's public API."

__version__ = "1.0-dev"

import sys
import warnings
from types import ModuleType

__all__ = ["install", "FancyModule"]

try:
    basestring
except NameError:
    basestring = str

class FancyModule(ModuleType):
    """A ModuleType subclass providing lazy imports and
    warn-on-attribute-access.

    If you add a module name to the __auto_import__ set it will be
    automatically imported on first access. (Note, however, that it is
    generally recommended that you not use this feature unless you have a real
    need for it, because if something goes wrong with your import then this
    can cause the error to be reported at a strange and confusing place.)

    If you do::

        __warn_on_access__[NAME] = (VALUE, WARNING OBJECT)

    then the given NAME will be accessible as an attribute on the module, with
    the given VALUE, and also raising the given WARNING OBJECT every time it
    is accessed.

    """

    def __metamodule_init__(self):
        # This method is like __init__, except that the weird way metamodule
        # objects are constructed means that we end up using
        # ModuleType.__init__, and our subclass __init__ never gets called. So
        # our setup code calls __metamodule_init__ explicitly. Do *not* call
        # ModuleType.__init__ from this method!
        self.__auto_import__ = set()
        self.__warn_on_access__ = {}

    def __getattr__(self, name):
        if name in self.__auto_import__:
            assert "." not in name
            __import__(self.__name__ + "." + name)
            return getattr(self, name)

        if name in self.__warn_on_access__:
            value, warning = self.__warn_on_access__[name]
            warnings.warn(warning, stacklevel=2)
            return value

        raise AttributeError(name)

    def __dir__(self):
        result = set(self.__dict__)
        result.update(self.__auto_import__)
        result.update(self.__warn_on_access__)
        return sorted(result)

    def __repr__(self):
        r = ModuleType.__repr__(self)
        # Older versions of ModuleType.__repr__ unconditionally say "<module
        # ...>" without taking the actual class into account.
        if r.startswith("<module "):
            r = "<%s%s" % (self.__class__.__name__,
                           r[len("<module"):])
        return r

def install(name, class_=FancyModule):
    """Install a metamodule class into the module with name 'name'.

    Generally used via the idiom::

        import metamodule
        metamodule.install(__name__)
        del metamodule

    By default it will use metamodule's built-in FancyModule type, but you can
    also specify your own ModuleType subclass if you want. Your subclass's
    __init__ method will *not* be called, but if you define a
    __metamodule_init__ method then it *will* be called.

    """

    orig_module = sys.modules[name]
    if isinstance(orig_module, class_):
        return
    try:
        orig_module.__class__ = class_
        new_module = orig_module
    except TypeError:
        new_module = _hacky_make_metamodule(orig_module, class_)
    if hasattr(new_module, "__metamodule_init__"):
        new_module.__metamodule_init__()
    sys.modules[name] = new_module

def _hacky_make_metamodule(orig_module, class_):
    # Construct the new module instance by hand, calling only ModuleType
    # methods, so as to simulate what happens in the __class__ assignment
    # path.
    new_module = ModuleType.__new__(class_)
    ModuleType.__init__(new_module, orig_module.__name__, orig_module.__doc__)

    # Now we jump through hoops to get at the module object guts...

    import ctypes
    # These are the only fields in the module object in CPython 1.0
    # through 2.7.
    fields = [
        ("PyObject_HEAD", ctypes.c_byte * object.__basicsize__),
        ("md_dict", ctypes.c_void_p),
    ]
    data_fields = ["md_dict"]
    # 3.0 adds PEP 3121 stuff:
    if (3,) <= sys.version_info:
        fields += [("md_def", ctypes.c_void_p),
                   ("md_state", ctypes.c_void_p),
               ]
        data_fields += ["md_def", "md_state"]
    # 3.4 adds md_weaklist and md_name
    if (3, 4) <= sys.version_info:
        fields += [("md_weaklist", ctypes.c_void_p),
                   ("md_name", ctypes.c_void_p),
                   ]
        # don't try to mess with md_weaklist, that seems unlikely to end
        # well.
        data_fields += ["md_name"]
    if (3, 5) <= sys.version_info:
        raise RuntimeError("Sorry, I can't read the future!")

    class CModule(ctypes.Structure):
        _fields_ = fields

    corig_module = ctypes.cast(id(orig_module), ctypes.POINTER(CModule))
    cnew_module = ctypes.cast(id(new_module), ctypes.POINTER(CModule))

    # And now we swap the two module's internal data fields. This makes
    # reference counting easier, plus prevents the destruction of orig_module
    # from cleaning up the objects we are still using.
    for data_field in data_fields:
        _swap_attr(corig_module.contents, cnew_module.contents, data_field)

    return new_module

def _swap_attr(obj1, obj2, attr):
    tmp1 = getattr(obj1, attr)
    tmp2 = getattr(obj2, attr)
    setattr(obj1, attr, tmp2)
    setattr(obj2, attr, tmp1)
