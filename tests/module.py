import metamodule
metamodule.install(__name__)
del metamodule

__warn_on_access__["a"] = (
    1,
    FutureWarning("'a' attribute will become 2 in next release"))
