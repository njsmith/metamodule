from metamodule import install
install(__name__)
del install

__auto_import__.add("submodule")

# Use a FutureWarning so that it's easier to see from the REPL that the
# warning is issued.
__warn_on_access__["a"] = (
    1,
    FutureWarning("'a' attribute will become 2 in next release"))

b = 2

def f(x):
    return 2 * x
