import inspect
from collections import namedtuple

Condition = namedtuple('Condition', ['check', 'message'])


def check(*conditions):
    def decorate(f):
        def g(*args, **kwargs):
            fargs = inspect.getcallargs(f, *args, **kwargs)

            for c in conditions:
                sig = inspect.signature(c.check)
                cargs = [fargs[param] for param in sig.parameters]

                if not c.check(*cargs):
                    raise ValueError(c.message)

            return f(*args, **kwargs)
        return g
    return decorate
