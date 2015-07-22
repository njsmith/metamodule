metamodule - Useful tools and gee-whiz tricks for defining Python APIs
======================================================================

In Python, writing a *metaclass* lets you create new kinds of class
objects whose behaviour you can control.

By analogy (and bit of abuse of English), writing a *metamodule* lets
you create module objects with customized behaviour.

``metamodule.py`` is a single-file, permissively-licensed Python
library that makes it easy and safe to use custom module subtypes as
the public interface for your library. For example, ordinarily in
Python it's easy to issue a deprecation warning when someone calls a
deprecated function (``mymodule.foo()``), but it's very difficult to
issue a deprecation warning when someone accesses a deprecated
constant (``mymodule.FOO``). Another commonly-requested (though
somewhat dangerous) feature is the ability to delay importing a
submodule until the first time it's accessed
(``mymodule.submodule.subfunction()``). With metamodule, these are
both easy to solve: we just give ``mymodule`` a custom ``__getattr__``
method that does what we want. (And in fact, you don't even need to
write this ``__getattr__`` -- metamodule includes an implementation
that provides both of the above features out-of-the-box.)


Example / documentation
=======================

In the source directory of this project, try starting a Python REPL
and running::

    >>> import examplepkg

``examplepkg`` is a module object::

    >>> import types
    >>> isinstance(examplepkg, types.ModuleType)
    True

But it's not a regular module object; it's a custom subclass::

    >>> examplepkg
    <FancyModule 'examplepkg' from 'examplepkg/__init__.py'>

And this subclass has superpowers::

    # Automatically loads the submodule on first access:
    >>> examplepkg.submodule.subattr
    ... submodule loading ...
    'look ma no import'

    # Imports are cached so future usage is just as fast as regular access:
    >>> examplepkg.submodule.subattr
    'look ma no import'

    # Accessing this attribute triggers a warning:
    >>> examplepkg.a
    __main__:1: FutureWarning: 'a' attribute will become 2 in next release
    1

    # But regular attributes continue to work fine, with no speed penalty:
    >>> examplepkg.b
    2

    # reload() works fine (except on CPython 3.3, which is buggy)
    >>> import imp
    >>> imp.reload(examplepkg)
    <FancyModule 'examplepkg' from 'examplepkg/__init__.pyc'>

    # And functions defined in the package use the same globals dict
    # as the package itself. (On py2 replace .__globals__ with .func_globals)
    >>> examplepkg.__dict__ is examplepkg.f.__globals__
    True

To accomplish this, all we had to do was put the following code at the
top of ``examplepkg/__init__.py``::

    # WARNING: this should be placed at the *very top* of your module,
    # *before* you import any code that might recursively re-import
    # your package.
    import metamodule
    metamodule.install(__name__)
    del metamodule

    # Any strings in this set name submodules that will be lazily imported:
    __auto_import__.add("submodule")
    # Attributes that we want to warn users about:
    __warn_on_access__["a"] = (
        # Attribute value
        1,
        # Warning issued when attribute is accessed
        FutureWarning("'a' attribute will become 2 in next release"))

You can also define your own ``ModuleType`` subclass and pass it as
the second argument to ``metamodule.install``. Your class can do
anything you can regularly do with a Python class -- define special
methods like ``__getattribute__``, use properties, have a custom
``__repr__``, whatever you want. Note that your class instance's
``__dict__`` will be the module globals dict, so assigning to
``self.foo`` is equivalent to creating a global variable in your
module named ``foo``, and vice-versa.

The one thing to watch out for is that your class's ``__init__`` will
*not* be called -- instead, you should define a method
``__metamodule_init__`` which will be called immediately after your
metamodule class is installed.


Versions supported
==================

Metamodule is currently tested against:

* CPython 2.6, 2.7
* CPython 3.2, 3.3, 3.4, and pre-releases of 3.5

I suspect it will *work* on pretty much every version of CPython that
has a working ``ctypes``, I just don't have convenient access to older
versions to test.

As far as I know we do not yet support PyPy, Jython, etc., but we will
as soon they catch up with Python 3.5 and start allowing ``__class__``
assignment on module objects.


How it works
============

Python has always allowed these kinds of tricks to some extent, via
the mechanism of assigning a new object to
``sys.modules["mymodule"]``; this object can then have whatever
behaviour you like. This can work well, but the end result is that you
have two different objects that both represent the same module: your
original module object (which owns the ``globals()`` namespace where
your module code executes), and your custom object. Depending on the
relative order of the assignment to ``sys.modules`` and imports of
submodules, you can end up with different pieces of code in the same
program thinking that ``mymodule`` refers to one or the other of these
objects. If they don't share the same ``__dict__``, then their
namespaces can get out of sync; alternatively, if they *do* share the
same ``__dict__``, then this means that your custom object can't
subclass ``ModuleType`` (module objects don't allow reassignment of
their ``__dict__`` attribute), which breaks ``reload()``. All in all
it's a bit of a mess. It's possible to write correct code using this
method, if you are extremely careful -- for example `apipkg
<https://pypi.python.org/pypi/apipkg/>`_ is a somewhat similar library
uses this approach, but to keep things workable it requires that your
library's public interface be defined *entirely* by apipkg
calls. There's no easy way to take a legacy Python package and
incrementally switch it over to using apipkg.

The key feature that metamodule provides is: it makes it easy to set
up ``sys.modules["mymodule"]`` so that it is both (a) an instance of a
class that you control, so you can have arbitrary properties etc.,
AND (b) a regular subclass of ``ModuleType`` with your
``__init__.py``'s ``globals()`` as its ``__dict__`` attribute, so that
you can continue using the usual Python approach to defining your
API.

This combination makes it easy and safe to transition an existing
library to using metamodule -- just add a call to
``metamodule.install`` at the top of your ``__init__.py``, and nothing
at all will change, except that you can now start taking advantage of
your new superpowers at your leisure.

How do we do it? On CPython 3.5 and later, this is easy: metamodule
uses ``__class__`` assignment on module objects (a feature that was
added to CPython explicitly to support this usage).

On CPython 3.4 and earlier, it uses ``ctypes`` hacks. These are ugly,
but safe so long as no one goes back in time and changes the internal
memory layout of module objects on old, already-released versions of
Python. (Which is not going to happen.) Basically, we instantiate a
new object of the specified ``ModuleType`` subclass, and then we use
some arcane knowledge of how these objects are laid out in order to
swap the guts of your original module and the new object. Then we
assign the new object into ``sys.modules``. This preserves the key
invariant that at any given point there's exactly one module that owns
your globals dict, and it's in ``sys.modules``. It does, however, mean
that things will go horribly wrong if you call ``metamodule.install``
*after* someone else has already imported your module. So unless you
only want to support Python 3.5+, then make sure to call
``metamodule.install`` right at the top of your module definition
file.

These two tricks together let us safely support all versions of
CPython, and as alternative implementations like PyPy catch up with
CPython 3.5 in supporting ``__class__`` assignment, we'll support
those too.
