from types import ModuleType

class MyModule(ModuleType):
    # No __metamodule_init__, to make sure that that's legal

    class_attr = "foo"

import metamodule
metamodule.install(__name__, MyModule)
del metamodule

other_attr = "bar"
