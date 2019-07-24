from collections import OrderedDict

import pytest

@pytest.fixture
def items():
    return [42, 'apple', object, 15, 'pear', str]

@pytest.fixture(params=[int, str, type])
def attr_class(request):
    return request.param

@pytest.fixture(params=['something'])
def attr_name(request):
    return request.param

def test_instance_tracker(items, attr_class, attr_name):
    from sprincl.tracker import InstanceTracker

    tracker = InstanceTracker(attr_class, attr_name)
    assert tracker.attr_name == attr_name
    assert tracker.attr_class == attr_class

    for n, item in enumerate(items):
        tracker['%02d' % n] = item
    # all target items were tracked
    assert list(tracker.tracked.values()) == [obj for obj in items if isinstance(obj, attr_class)]
    # all non-target items were stored in __dict__
    assert all(obj in tracker.values() for obj in items if not isinstance(obj, attr_class))
    # no target item was stored in __dict__
    assert all(obj not in tracker.values() for obj in items if isinstance(obj, attr_class))

def test_meta_tracker(items, attr_class, attr_name):
    from sprincl.tracker import MetaTracker

    MyMetaTracker = MetaTracker.sub('MyMetaTracker', attr_class, attr_name)

    class_args = ('MyTracker', (object,))
    # emulate the class body being executed
    class_dict = MyMetaTracker.__prepare__(*class_args)
    for n, item in enumerate(items):
        class_dict['%02d' % n] = item
    MyTracker = MyMetaTracker(*class_args, class_dict)

    assert hasattr(MyTracker, attr_name)

    # all target items were tracked
    assert list(getattr(MyTracker, attr_name).values()) == [obj for obj in items if isinstance(obj, attr_class)]
    # all non-target items were stored in __dict__
    assert all(obj in MyTracker.__dict__.values() for obj in items if not isinstance(obj, attr_class))
    # no target item was stored in __dict__
    assert all(obj not in MyTracker.__dict__.values() for obj in items if isinstance(obj, attr_class))
