import pytest

from sprincl.base import Param


class TestParam(object):
    def test_instatiation(self):
        Param(object)

    def test_dtype_not_assigned(self):
        with pytest.raises(TypeError):
            Param()

    def test_dtype_no_type(self):
        with pytest.raises(TypeError):
            Param('monkey')

    def test_dtype_multiple(self):
        param = Param((object, type))
        assert param.dtype == (object, type)

    def test_dtype_single_to_tuple(self):
        param = Param(object)
        assert param.dtype == (object,)
