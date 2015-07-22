from types import ModuleType

class MyModule(ModuleType):
    def __metamodule_init__(self):
        self._metamodule_init_called = True

    class_attr = "foo"

import metamodule
metamodule.install(__name__, MyModule)
del metamodule

other_attr = "bar"
