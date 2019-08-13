"""Test tracker functionalities.

"""

import pytest

from sprincl.tracker import InstanceTracker, MetaTracker


@pytest.fixture(scope='module')
def items():
    return [42, 'apple', object, 15, 'pear', str]


@pytest.fixture(scope='module', params=[int, str, type])
def attr_class(request):
    return request.param


@pytest.fixture(scope='module', params=['something'])
def attr_name(request):
    return request.param


@pytest.fixture(scope='module')
def instance_tracker(items, attr_class, attr_name):
    tracker = InstanceTracker(attr_class, attr_name)
    for n, item in enumerate(items):
        tracker['%02d' % n] = item
    return tracker


@pytest.fixture(scope='module')
def meta_tracker(attr_class, attr_name):
    MyMetaTracker = MetaTracker.sub('MyMetaTracker', attr_class, attr_name)
    return MyMetaTracker


@pytest.fixture(scope='module')
def tracker(meta_tracker, items):
    MyMetaTracker = meta_tracker

    class_args = ('MyTracker', (object,))
    # emulate the class body being executed
    class_dict = MyMetaTracker.__prepare__(*class_args)
    for n, item in enumerate(items):
        class_dict['%02d' % n] = item
    MyTracker = MyMetaTracker(*class_args, class_dict)

    return MyTracker


class TestInstanceTracker(object):
    def test_attributes(self, tracker, attr_name, attr_class):
        """Crucial attributes set"""
        assert tracker.attr_name == attr_name
        assert tracker.attr_class == attr_class

    def test_target_tracked(self, instance_tracker, items, attr_name, attr_class):
        """All target items tracked"""
        assert list(instance_tracker.tracked.values()) == [obj for obj in items if isinstance(obj, attr_class)]

    def test_non_target_dict(self, instance_tracker, items, attr_name, attr_class):
        """All non-target items stored in __dict__"""
        assert all(obj in instance_tracker.values() for obj in items if not isinstance(obj, attr_class))

    def test_target_not_dict(self, instance_tracker, items, attr_name, attr_class):
        """no target item stored in __dict__"""
        assert all(obj not in instance_tracker.values() for obj in items if isinstance(obj, attr_class))


class TestMetaTracker(object):
    def test_attributes(self, tracker, attr_name):
        """Crucial attributes set"""
        assert hasattr(tracker, attr_name)

    def test_target_tracked(self, tracker, items, attr_name, attr_class):
        """All target items tracked"""
        assert list(getattr(tracker, attr_name).values()) == [obj for obj in items if isinstance(obj, attr_class)]

    def test_non_target_dict(self, tracker, items, attr_name, attr_class):
        """All non-target items stored in __dict__"""
        assert all(obj in tracker.__dict__.values() for obj in items if not isinstance(obj, attr_class))

    def test_target_not_dict(self, tracker, items, attr_name, attr_class):
        """no target item stored in __dict__"""
        assert all(obj not in tracker.__dict__.values() for obj in items if isinstance(obj, attr_class))
