"""Test tracker functionalities.

"""

import pytest

from sprincl.tracker import Tracker


@pytest.fixture(scope='module')
def tracked():
    class SubTracked(Tracker):
        attr_1 = 42
        attr_2 = 'apple'
        attr_3 = object
        attr_4 = 15
        attr_5 = 'pear'
        attr_6 = str
    return SubTracked


@pytest.fixture(scope='module')
def values():
    result = dict(
        attr_1=42,
        attr_2='apple',
        attr_3=object,
        attr_4=15,
        attr_5='pear',
        attr_6=str
    )
    return result


@pytest.fixture(scope='module')
def attributes(tracked):
    result = dict(
        attr_1='value_1',
        attr_2='value_2',
        attr_3='value_3',
        attr_4='value_4',
        attr_5='value_5',
        attr_6='value_6',
    )
    return result


@pytest.fixture(scope='module')
def instance(tracked, attributes):
    result = tracked()
    for key, value in attributes.items():
        setattr(result, key, value)
    return result


class TestTracker(object):
    def test_collect(self, tracked):
        assert tracked.collect(int) == dict(attr_1=42, attr_4=15)
        assert tracked.collect(str) == dict(attr_2='apple', attr_5='pear')
        assert tracked.collect(type) == dict(attr_3=object, attr_6=str)

    def test_collect_multiple(self, tracked, values):
        assert tracked.collect((int, str, type)) == values

    def test_collect_attr(self, instance, attributes):
        assert instance.collect_attr((int, str, type)) == attributes
