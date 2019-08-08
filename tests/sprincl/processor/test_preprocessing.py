import numpy as np
import pytest

from sprincl.processor.preprocessing import Rescale, Resize, Pooling


@pytest.fixture
def data():
    return np.ones((10, 8, 8))


def test_rescaling(data):
    proc = Rescale(scale=0.5)
    out = proc(data)
    assert out.shape == (data.shape[0], 4, 4)


def test_resizing(data):
    proc = Resize(width=16, height=4)
    out = proc(data)
    assert out.shape == (data.shape[0], 4, 16)


def test_pooling(data):
    proc = Pooling(stride=(1, 2, 2), pooling_function=np.sum)
    out = proc(data)
    assert out.shape == (data.shape[0], 4, 4)
    np.testing.assert_equal(out, 4 * np.ones(out.shape))
