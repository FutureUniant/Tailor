

class Register:
    """A registry to map strings to classes.

    Args:
        name (str): Registry name.
    """

    def __init__(self, name):
        self._name = name
        self._module_dict = dict()

    @property
    def name(self):
        return self._name

    @property
    def module_dict(self):
        return self._module_dict

    def get(self, key):
        return self._module_dict.get(key, None)

    def set(self, key, value):
        self._module_dict[key] = value

    def contains(self, key):
        return key in self._module_dict.keys()

    def register(self, target=None, name=None, force=False):
        """Register a module.

        A record will be added to `self._module_dict`, whose key is the class
        name or the specified name, and value is the class itself.
        It can be used as a decorator or a normal function.

        Args:
            target (callable| class | None): The target for register.
            name (str | None): The module name to be registered. If not
                specified, the class name will be used.
            force (bool, optional): Whether to override an existing class with
                the same name. Default: False.
        """
        if not isinstance(force, bool):
            raise TypeError(f"force must be a boolean, but got {type(force)}")

        # raise the error ahead of time
        if not (name is None or isinstance(name, str)):
            raise TypeError(f"name must be a str, but got {type(name)}")

        def _wrap_register(func):
            return self.register(target=func, name=name, force=force)

        if target is None:
            return _wrap_register

        if name is None:
            name = target.__name__

        if self.contains(name) and not force:
            raise ValueError(f"Name must be unique, but {name} isn't unique.")

        self.set(name, target)
        return target


ALGORITHM = Register(name="algorithm")


def build_algorithm(name):
    return ALGORITHM.get(name)
