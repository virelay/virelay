import pytest

from sprincl.processor.base import Processor, Param


class TestProcessor(Processor):
    param = Param(str, mandatory=True)
    param2 = Param(int)


def test_processor_mandatory_param():
    with pytest.raises(ValueError):
        TestProcessor()


def test_processor_wrong_type_param():
    with pytest.raises(TypeError):
        TestProcessor(param=2)


def test_processor_creation():
    TestProcessor(param="neki")


def test_processor_bad_dtype():
    with pytest.raises(ValueError):
        class TestProcessor1(Processor):
            param = Param(2)
