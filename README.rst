metamodule
==========

An experiment with Python "metamodules". Should work with CPython 2.7
through 3.4.

Earlier versions can be easily made to work in principle, I was just
too lazy to deal with Python 2.6 and earlier's import API.

Later versions are currently unsupported because the ``ctypes``
hackery requires knowledge of some of CPython's internal data
structures.  Hopefully, 3.5+ will add support for assignment to a
module object's __class__ field, in which case this code should Just
Work. (A similar comment applies to PyPy etc.)

Example
=======

Try starting a Python REPL and typing::

    >>> import examplepkg

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

The guts are in ``metamodule.py``; see ``examplepkg/`` for example usage.
