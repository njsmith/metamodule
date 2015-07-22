from types import ModuleType

class MyModule(ModuleType):
    def __metamodule_init__(self):
        self._metamodule_init_called = True

    class_attr = "foo"

from metamodule import install
install(__name__, MyModule)
del install

other_attr = "bar"
