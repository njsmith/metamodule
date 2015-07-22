# This is part of metamodule.
# Copyright (C) 2014-2015 Nathaniel J. Smith <njs@pobox.com>
# Released under a 2-clause BSD license; see the LICENSE file for details.

import sys
import warnings

# reload is:
#   Python 2: builtin
#   Python 3.0-3.3: imp.reload
#   Python 3.4+: importlib.reload
try:
    reload
except NameError:
    try:
        from importlib import reload
    except ImportError:
        from imp import reload

import metamodule

def test_metamodule_general():
    import package

    assert isinstance(package, metamodule.FancyModule)

    assert repr(package).startswith("<FancyModule ")

    assert "submodule" in dir(package)
    assert "a" in dir(package)
    assert "b" in dir(package)

    assert isinstance(package.submodule.subattr, str)

    assert package.b == 2
    with warnings.catch_warnings(record=True) as log:
        warnings.simplefilter("always")
        assert package.a == 1

    assert len(log) == 1
    assert log[0].category is FutureWarning

    # Make sure reload() doesn't raise an error.
    # Unfortunately CPython 3.3 refuses to allow reload() on any object who
    # type is not *exactly* ModuleType. All other Python versions should
    # work.
    if sys.version_info[:2] != (3, 3):
        reload(package)

# Test a module (as opposed to a package)
def test_metamodule_module():
    import module

    assert isinstance(module, metamodule.FancyModule)

    with warnings.catch_warnings(record=True) as log:
        warnings.simplefilter("always")
        assert module.a == 1

    assert len(log) == 1
    assert log[0].category is FutureWarning

def test_metamodule_custom():
    import module_custom, module_custom2

    assert module_custom._metamodule_init_called is True

    for mod in [module_custom, module_custom2]:
        assert isinstance(mod, mod.MyModule)
        assert mod.class_attr == "foo"
        assert mod.other_attr == "bar"
