# -*- coding: utf-8 -*-

from collections import namedtuple

from yaggy.utils import pick


def test_pick_returns_none_for_missing_key():

    ctx = {'key': 'value'}
    paths = ('foo', 'foo.baz', 'foo.baz.bar')

    for p in paths:
        res = pick(ctx, p)
        assert res is None


def test_pick_returns_proper_nested_dict_value():

    ctx = {'foo': {'baz': 'bar'}}
    path = 'foo.baz'

    assert pick(ctx, path) == 'bar'


def test_pick_returns_attr_value():

    Obj = namedtuple('Obj', ['bar'])
    o = Obj(bar='test')

    ctx = {'foo': {'baz': o}}
    path = 'foo.baz.bar'

    assert pick(ctx, path) == 'test'
