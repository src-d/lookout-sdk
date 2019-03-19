import importlib
from contextlib import contextmanager

import unittest


@contextmanager
def spy_func(target):
    module_name, func_name = target.rsplit(".", 1)
    func = getattr(importlib.import_module(module_name), func_name)
    with unittest.mock.patch(target, wraps=func) as mocked:
        yield mocked
