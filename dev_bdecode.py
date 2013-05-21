#! encoding: utf-8
"""A silly lookahead parser for Bencode with support for incomplete or excess data."""

import StringIO
import os

class IncompleteInput(Exception):
    pass

class Lookahead(object):
    def __init__(self, f):
        self._source = f
        self._peek = None

    def peek(self):
        if self._peek is None:
            self._peek = self._source.read(1)
        return self._peek

    def read(self, n):
        left = n
        buf = []
        if self._peek:
            buf.append(self._peek)
            self._peek = None
            left -= 1
        while True:
            if left == 0:
                break
                raise IncompleteInput()
            chunk = self._source.read(left)
            if not chunk:
                raise IncompleteInput
            left -= len(chunk)
            buf.append(chunk)
        return "".join(buf)


def decode_int(wrapper):
    assert wrapper.read(1) == 'i'
    sign = 1
    if wrapper.peek() == '-':
        sign = -1
        wrapper.read(1)

    num = 0
    while True:
        ch = wrapper.read(1)

        if '0' <= ch <= '9':
            num = 10 * num + (ord(ch) - ord('0'))
        elif ch == 'e':
            break
        else:
            raise ValueError('unexpected char in decode_int %s' % ch)
    return sign * num


def decode_str(wrapper):
    num = 0
    while True:
        ch = wrapper.read(1)
        if ch == ":":
            break
        num = 10 * num + (ord(ch) - ord('0'))
    res = wrapper.read(num)
    return res


def decode_list(wrapper):
    assert wrapper.read(1) == 'l'
    res = []
    while True:
        ch = wrapper.peek()
        if ch == 'e':
            wrapper.read(1)
            break
        res.append(decode_one(wrapper))
    return res


def decode_dict(wrapper):
    assert wrapper.read(1) == 'd'
    res = {}
    while True:
        ch = wrapper.peek()
        if ch == 'e':
            wrapper.read(1)
            break
        key = decode_str(wrapper)
        value = decode_one(wrapper)
        res[key] = value
    return res


def decode_one(wrapper):
    ch = wrapper.peek()
    if ch == 'i':
        return decode_int(wrapper)
    # size spec
    if '0' <= ch <= '9':
        return decode_str(wrapper)
    if ch == 'l':
        return decode_list(wrapper)

    if ch == 'd':
        return decode_dict(wrapper)

#    raise ValueError("Invalid prefix character in bdecode stream (%s)" % ch)

def loads(s):
    """
    >>> loads(bencode.bencode(1))
    (1, None)
    >>> loads(bencode.bencode('foobar'))
    ('foobar', None)
    >>> loads(bencode.bencode([100, 200]))
    ([100, 200], None)
    >>> loads(bencode.bencode(1) + bencode.bencode(2))
    (1, 'i2e')
    >>> loads(bencode.bencode(1) + "20ssss")
    (1, '20ssss')
    >>> loads('3:aaa2:bb3:ccc')
    ('aaa', '2:bb3:ccc')
    >>> loads(bencode.bencode({'foo': 'bar', 'cat': 'fish'}) + '100:abcd')
    ({'foo': 'bar', 'cat': 'fish'}, '100:abcd')
    >>> loads('d3:cat4:fish3:dog10:whargharbl3:foo')
    (None, 'd3:cat4:fish3:dog10:whargharbl3:foo')
    """
    sio = StringIO.StringIO(s)
    buf = Lookahead(sio)
    try:
        result = decode_one(buf)
        if (sio.tell() != len(s)):
            return result, sio.read()
    except IncompleteInput:
        return None, sio.getvalue()

    return result, None

def load(f):
    buf = Lookahead(f)
    return decode_one(buf)

if __name__ == '__main__':
    import doctest
    import bencode

    doctest.testmod()
    exit()

    import bencode
    import StringIO

    def test(d):
        return
        s = bencode.bencode(d)
        sio = StringIO.StringIO(s)
        buf = Lookahead(sio)
        #w = Wrapper(io)
        out = decode_one(buf)
        assert d == out, "%s %s" % (d, out)

    def test_raw(raw, exp):
        sio = StringIO.StringIO(raw)
        buf = Lookahead(sio)
        out = decode_one(buf)
        assert exp == out, "%s %s" % (exp, out)

    test(1)
    test(12123123)
    test("abc")
    test("safdasdfasdfqwefsdfqwfe")

    test([1, 2, 3, 4, 5])

    test([])

    test({})
    test({"hello": 12})
    test(-12)
    test(0)
    test(-1)

    test(u"zażółć".encode("utf-8"))

#    test_raw("1ae", 1)

    print "ok"
    print loads("d3:cat4:fish3:dog10:whargharbl3:foo3:bared3:cat4")