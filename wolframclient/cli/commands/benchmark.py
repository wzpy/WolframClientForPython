# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import os
import tempfile

from wolframclient.cli.utils import SimpleCommand
from wolframclient.language import wl
from wolframclient.serializers import export
from wolframclient.utils.debug import timed
from wolframclient.utils.decorators import to_tuple
from wolframclient.utils.encoding import force_text
from wolframclient.utils.functional import first

import decimal

@to_tuple
def repeat(el, n = 1):
    for i in range(n):
        yield el

class Command(SimpleCommand):

    col_size = 8
    repetitions = 10
    complexity = [1, 2, 5, 10, 100, 1000]

    def complexity_handler(self, complexity):
        return {
            'symbols': repeat(wl.Symbol, complexity),
            'strings': repeat("string", complexity),
            'bytes': repeat(b"bytes", complexity),
            'integers': repeat(1, complexity),
            'decimals': repeat(decimal.Decimal('1.23'), complexity),
            'floats': repeat(1.23, complexity),
            'dict': repeat({1:2, 3:4, 5:6}, complexity),
            'list': repeat([1, 2, 3], complexity),
            'functions': repeat(wl.Function(1, 2, 3), complexity),
        }

    @timed
    def export(self, *args, **opts):
        return export(*args, **opts)

    def formatted_time(self, *args, **opts):

        time = sum(
            first(self.export(*args, **opts)) for i in range(self.repetitions))

        return '%.5f' % (time / self.repetitions)

    def table_line(self, *iterable):
        self.print(*(force_text(c).ljust(self.col_size) for c in iterable))

    def table_divider(self, length):
        self.print(*("-" * self.col_size for i in range(length)))

    def handle(self, *args):

        path = tempfile.gettempdir()

        benchmarks = [(c, self.complexity_handler(c)) for c in self.complexity]

        self.print('dumping results in', path)

        self.table_line(
            "", *(force_text(c).ljust(self.col_size) for c in self.complexity))
        self.table_divider(len(self.complexity) + 1)

        for export_format, opts in (
            ("wl", dict()),
            ("wxf", dict()),
            ("wxf", dict(compress=True)),
        ):
            self.table_line(
                export_format,
                *(self.formatted_time(
                    expr,
                    stream=os.path.join(
                        path, 'benchmark-test-%s.%s' %
                        (force_text(complexity).zfill(7), export_format)),
                    target_format=export_format,
                    **opts) for complexity, expr in benchmarks))

        self.table_line()
