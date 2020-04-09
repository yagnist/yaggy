# -*- coding: utf-8 -*-

from collections import namedtuple

from yaggy import utils as u


def test_returns_none_for_missing_key():

    ctx = {'key': 'value'}
    paths = ('foo', 'foo.baz', 'foo.baz.bar')

    for p in paths:
        res = u.pick(ctx, p)
        assert res is None


def test_returns_proper_nested_dict_value():

    ctx = {'foo': {'baz': 'bar'}}
    path = 'foo.baz'

    assert u.pick(ctx, path) == 'bar'


def test_returns_attr_value():

    Obj = namedtuple('Obj', ['bar'])
    o = Obj(bar='test')

    ctx = {'foo': {'baz': o}}
    path = 'foo.baz.bar'

    assert u.pick(ctx, path) == 'test'
