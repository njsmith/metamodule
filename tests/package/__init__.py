# Setup the metamodule.
import metamodule
metamodule.install(__name__)
del metamodule

# Automatically execute "import .submodule" the first time that someone tries
# to access it:
__auto_import__.add("submodule")

# Issue a warning whenever "a" is accessed.
# We use a FutureWarning so that it's easier to see from the REPL that the
# warning is issued.
__warn_on_access__["a"] = (
    1,
    FutureWarning("'a' attribute will become 2 in next release"))

# Regular globals are still exposed and accessible with no speed penalty:
b = 2
def f(x):
    return b * x
