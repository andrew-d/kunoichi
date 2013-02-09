from io import BytesIO
from collections import defaultdict, Iterable

import textwrap
import re

__all__ = ['Task', 'config', 'do_config']


# The following code is taken from ninja_syntax.py, which is provided
# with the Ninja source code.
# See: https://github.com/martine/ninja/blob/master/misc/ninja_syntax.py
# ----------------------------------------------------------------------
def escape_path(word):
    return word.replace('$ ','$$ ').replace(' ','$ ').replace(':', '$:')


def escape(string):
    """Escape a string such that it can be embedded into a Ninja file without
    further interpretation."""
    assert '\n' not in string, 'Ninja syntax does not allow newlines'
    # We only have one special metacharacter: '$'.
    return string.replace('$', '$$')


class Writer(object):
    def __init__(self, output, width=78):
        self.output = output
        self.width = width

    def newline(self):
        self.output.write('\n')

    def comment(self, text):
        for line in textwrap.wrap(text, self.width - 2):
            self.output.write('# ' + line + '\n')

    def variable(self, key, value, indent=0):
        if value is None:
            return
        if isinstance(value, list):
            value = ' '.join(filter(None, value))  # Filter out empty strings.
        self._line('%s = %s' % (key, value), indent)

    def pool(self, name, depth):
        self._line('pool %s' % name)
        self.variable('depth', depth, indent=1)

    def rule(self, name, command, description=None, depfile=None,
             generator=False, pool=None, restat=False, rspfile=None,
             rspfile_content=None):
        self._line('rule %s' % name)
        self.variable('command', command, indent=1)
        if description:
            self.variable('description', description, indent=1)
        if depfile:
            self.variable('depfile', depfile, indent=1)
        if generator:
            self.variable('generator', '1', indent=1)
        if pool:
            self.variable('pool', pool, indent=1)
        if restat:
            self.variable('restat', '1', indent=1)
        if rspfile:
            self.variable('rspfile', rspfile, indent=1)
        if rspfile_content:
            self.variable('rspfile_content', rspfile_content, indent=1)

    def build(self, outputs, rule, inputs=None, implicit=None, order_only=None,
              variables=None):
        outputs = self._as_list(outputs)
        all_inputs = self._as_list(inputs)[:]
        out_outputs = list(map(escape_path, outputs))
        all_inputs = list(map(escape_path, all_inputs))

        if implicit:
            implicit = map(escape_path, self._as_list(implicit))
            all_inputs.append('|')
            all_inputs.extend(implicit)
        if order_only:
            order_only = map(escape_path, self._as_list(order_only))
            all_inputs.append('||')
            all_inputs.extend(order_only)

        self._line('build %s: %s' % (' '.join(out_outputs),
                                        ' '.join([rule] + all_inputs)))

        if variables:
            if isinstance(variables, dict):
                iterator = iter(variables.items())
            else:
                iterator = iter(variables)

            for key, val in iterator:
                self.variable(key, val, indent=1)

        return outputs

    def include(self, path):
        self._line('include %s' % path)

    def subninja(self, path):
        self._line('subninja %s' % path)

    def default(self, paths):
        self._line('default %s' % ' '.join(self._as_list(paths)))

    def _count_dollars_before_index(self, s, i):
      """Returns the number of '$' characters right in front of s[i]."""
      dollar_count = 0
      dollar_index = i - 1
      while dollar_index > 0 and s[dollar_index] == '$':
        dollar_count += 1
        dollar_index -= 1
      return dollar_count

    def _line(self, text, indent=0):
        """Write 'text' word-wrapped at self.width characters."""
        leading_space = '  ' * indent
        while len(leading_space) + len(text) > self.width:
            # The text is too wide; wrap if possible.

            # Find the rightmost space that would obey our width constraint and
            # that's not an escaped space.
            available_space = self.width - len(leading_space) - len(' $')
            space = available_space
            while True:
              space = text.rfind(' ', 0, space)
              if space < 0 or \
                 self._count_dollars_before_index(text, space) % 2 == 0:
                break

            if space < 0:
                # No such space; just use the first unescaped space we can find.
                space = available_space - 1
                while True:
                  space = text.find(' ', space + 1)
                  if space < 0 or \
                     self._count_dollars_before_index(text, space) % 2 == 0:
                    break
            if space < 0:
                # Give up on breaking.
                break

            self.output.write(leading_space + text[0:space] + ' $\n')
            text = text[space+1:]

            # Subsequent lines are continuations, so indent them.
            leading_space = '  ' * (indent+2)

        self.output.write(leading_space + text + '\n')

    def _as_list(self, input):
        if input is None:
            return []
        if isinstance(input, list):
            return input
        return [input]

# ----------------------------------------------------------------------

class _attrdict(defaultdict):
    """A simple autovivifying dict()"""
    def __getattr__(self, key): return self[key]
    def __setattr__(self, key, val): self[key]=val

def attrdict():
    """A simple autovivifying dict()"""
    return _attrdict(attrdict)


_config_functions = []
def config(func):
    """
    This function defines a configuration method that is called before any
    build rules are generated.
    """
    _config_functions.append(func)
    return func


def do_config():
    """
    Run all configuration functions in the order they were defined.
    """
    config_obj = attrdict()
    for func in _config_functions:
        func(config_obj)

    return config_obj


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

            # Get the rule.
            cmd = func(config)
            cmd = cmd.format(cfg=config)
            writer.rule(func.__name__, cmd, **kwargs)

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

