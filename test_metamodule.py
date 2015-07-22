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
import examplepkg

def test_metamodule():
    assert isinstance(examplepkg, metamodule.FancyModule)

    assert repr(examplepkg).startswith("<FancyModule ")

    assert "submodule" in dir(examplepkg)
    assert "a" in dir(examplepkg)
    assert "b" in dir(examplepkg)

    assert isinstance(examplepkg.submodule.subattr, str)

    assert examplepkg.b == 2
    with warnings.catch_warnings(record=True) as log:
        warnings.simplefilter("always")
        assert examplepkg.a == 1

    assert len(log) == 1
    assert log[0].category is FutureWarning

    # Make sure reload() doesn't raise an error.
    # Unfortunately CPython 3.3 refuses to allow reload() on any object who
    # type is not *exactly* ModuleType. All other Python versions should
    # work.
    if sys.version_info[:2] != (3, 3):
        reload(examplepkg)
