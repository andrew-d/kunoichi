from io import BytesIO
from collections import Iterable

import ninja_syntax as ns

_config_functions = []

def config(func):
    """
    This function defines a configuration method that is called before any
    build rules are generated.
    """
    _config_functions.append(func)
    return func


class Task(object):
    """
    This class represents a task.  Each defined task will be written to a
    different .ninja file.  The empty task (i.e. one with no name, or a blank
    name) is the one that will be run by default.
    """

    def __init__(self, name=None):
        if name is None:
            name = ''

        self.name = name
        self.funcs = []
        self.rules = []

    def build(self, func):
        """
        Define a function that is called to generate build rules.
        """
        self.funcs.append(func)
        return func

    def rule(self, func=None, **kwargs):
        """
        Define a function that is called to make a rule.
        """
        if hasattr(func, '__call__'):
            self.rules.append((func, {}))
            return func
        else:
            def _wrapper(func):
                self.rules.append((func, kwargs))
                return func

            return _wrapper

    def generate(self, config):
        """
        Generate a ninja build file, returning the value as a string.
        """
        buff = BytesIO()
        writer = ns.Writer(buff)

        # Generate all rules.
        for func, kwargs in self.rules:
            # Get the description from the docstring, if it doesn't exist.
            desc = kwargs.pop('description', None)
            if desc is None:
                desc = func.__doc__ if func.__doc__ is not None else ''
            kwargs['description'] = desc

            # Write the actual rule.
            writer.rule(func.__name__, func(config), **kwargs)

        # Generate all build rules.
        for func in self.funcs:
            self._add_build(writer, func(config))

        buff.seek(0)
        return buff.read()

    def _add_build(self, writer, val):
        # The value returned should be a list or tuple.
        assert isinstance(val, Iterable)

        # For each rule.
        for b in val:
            if isinstance(b, dict):
                outputs = b.pop('outputs')
                rule = b.pop('rule')

                writer.build(outputs, rule, **b)

            elif isinstance(b, (list, tuple)):
                outputs = b[0]
                rule = b[1]

                inputs = b[2] if len(b) > 2 else None
                implicit = b[3] if len(b) > 3 else None
                order_only = b[4] if len(b) > 4 else None
                variables = b[5] if len(b) > 5 else None

                writer.build(outputs, rule, inputs=inputs, implicit=implicit,
                             order_only=order_only, variables=variables)

