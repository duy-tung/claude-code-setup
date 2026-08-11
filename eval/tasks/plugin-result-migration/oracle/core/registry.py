"""Name -> plugin instance registry."""

REGISTRY = {}


def register(name):
    """Decorator registration."""
    def wrap(cls):
        cls.name = name
        REGISTRY[name] = cls()
        return cls
    return wrap


def register_by_name(name, cls):
    """Imperative registration for plugins that cannot use the decorator."""
    cls.name = name
    REGISTRY[name] = cls()
    return cls


def get(name):
    return REGISTRY[name]


def names():
    return sorted(REGISTRY)
