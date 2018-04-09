# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from wolframclient.serializers.base import FormatSerializer

from itertools import chain

from wolframclient.serializers.escape import py_encode_text
from wolframclient.utils.encoding import force_bytes

import base64

def yield_with_separators(iterable, separator = b', ', first = None, last = None):
    if first:
        yield first
    for i, arg in enumerate(iterable):
        if i:
            yield separator
        for sub in arg:
            yield sub
    if last:
        yield last

class WLSerializer(FormatSerializer):

    def __init__(self, normalizer = None, indent = None, **opts):
        super(WLSerializer, self).__init__(normalizer = normalizer, **opts)
        self.indent = indent

    def dump(self, data, stream):
        for payload in self.normalize(data):
            stream.write(payload)
        return stream


    def serialize_function(self, head, args):
        return chain(
            head,
            yield_with_separators(args, first = b'[', last = b']')
        )

    def serialize_symbol(self, name):
        yield force_bytes(name)

    def serialize_string(self, string):
        return py_encode_text(string)

    def serialize_bytes(self, obj):
        return self.serialize_function(
            self.serialize_symbol('ByteArray'), (
                ('"', base64.b64encode(bytes), '"'),
            )
        )

    def serialize_decimal(self, number):
        yield ('{0:f}'.format(number)).encode('utf-8')

    def serialize_float(self, number):
        yield ('{0:f}'.format(number)).encode('utf-8')

    def serialize_integer(self, number):
        yield ('%i' % number).encode('utf-8')

    def serialize_rule(self, lhs, rhs):
        return yield_with_separators(
            (lhs, rhs),
            separator = b' -> '
        )

    def serialize_rule_delayed(self, lhs, rhs):
        return yield_with_separators(
            (lhs, rhs),
            separator = b' :> '
        )

    def serialize_mapping(self, mapping):
        return yield_with_separators((
                self.serialize_rule(key, value)
                for key, value in mapping
            ),
            first = b'<|',
            last  = b'|>'
        )

    def serialize_iterable(self, iterable):
        return yield_with_separators(
            iterable,
            first = b'{',
            last  = b'}'
        )