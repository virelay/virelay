import numpy as np
import pytest

from sprincl.processor.preprocessing import Rescale, Resize, Pooling


@pytest.fixture
def no_channels():
    return np.ones((10, 8, 8))


@pytest.fixture
def channels_first():
    return np.ones((10, 3, 8, 8))


@pytest.fixture
def channels_last():
    return np.ones((10, 8, 8, 3))


@pytest.fixture
def random_noise():
    return np.random.normal(0, 1, (10, 8, 8))


@pytest.mark.parametrize('data,shape', [('random_noise', (10, 4, 4)),
                                        ('channels_first', (10, 3, 4, 4)),
                                        ('channels_last', (10, 4, 4, 3))])
def test_rescaling(data, shape, request):
    proc = Rescale(scale=0.5, channels_first=data == 'channels_first')
    data = request.getfixturevalue(data)
    out = proc(data)
    assert out.shape == shape
    assert data.max() >= out.max()
    assert data.min() <= out.min()


@pytest.mark.parametrize('data,shape', [('random_noise', (10, 4, 16)),
                                        ('channels_first', (10, 3, 4, 16)),
                                        ('channels_last', (10, 4, 16, 3))])
def test_resizing(data, shape, request):
    proc = Resize(width=16, height=4, channels_first=data == 'channels_first')
    data = request.getfixturevalue(data)
    out = proc(data)
    assert out.shape == shape
    assert data.max() >= out.max()
    assert data.min() <= out.min()


@pytest.mark.parametrize('data,shape,stride', [('no_channels', (10, 4, 4), (1, 2, 2)),
                                               ('channels_first', (10, 3, 4, 4), (1, 1, 2, 2)),
                                               ('channels_last', (10, 4, 4, 3), (1, 2, 2, 1))])
def test_pooling(data, shape, stride, request):
    proc = Pooling(stride=stride, pooling_function=np.sum)
    data = request.getfixturevalue(data)
    out = proc(data)
    assert out.shape == shape
    np.testing.assert_equal(out, 4 * np.ones(out.shape))
