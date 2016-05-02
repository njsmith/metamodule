from types import ModuleType

class MyModule(ModuleType):
    # Make sure that having no __metamodule_init__ is legal, and does not get
    # routed through __getattr__.

    def __getattr__(self, attr):
        if attr == "class_attr":
            return "foo"
        raise AttributeError

import metamodule
metamodule.install(__name__, MyModule)
del metamodule

other_attr = "bar"
