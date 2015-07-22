from metamodule import install
install(__name__)
del install

__warn_on_access__["a"] = (
    1,
    FutureWarning("'a' attribute will become 2 in next release"))
