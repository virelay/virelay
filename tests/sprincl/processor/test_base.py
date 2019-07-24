import pytest

from sprincl.processor.base import Processor, Param


@pytest.fixture(scope='module')
def processor_type():
    class MyProcessor(Processor):
        param_1 = Param(str, mandatory=True)
        param_2 = Param(int, -25)
        param_3 = Param((str, int))
        value = 42
        text = 'apple'

        def function(self, data):
            return 21

    return MyProcessor


@pytest.fixture(scope='module')
def kwargs(processor_type):
    kwargs = {
        'is_output': False,
        'is_checkpoint': False,
        'param_1': 'stuff',
        'param_2': 5,
        'param_3': 6,
    }
    return kwargs


class TestProcessor(object):
    def test_params_tracked(self, processor_type):
        assert ['is_output', 'is_checkpoint', 'param_1', 'param_2', 'param_3'] == list(processor_type.params)

    def test_params_no_attributes(self, processor_type):
        assert not any(hasattr(processor_type, name) for name in ('param_1', 'param_2'))

    def test_creation(self, processor_type):
        processor_type(param_1="neki")

    def test_instance_assign(self, processor_type, kwargs):
        processor = processor_type(**kwargs)
        assert all(getattr(processor, key) == val for key, val in kwargs.items())

    def test_instance_default(self, processor_type):
        processor = processor_type(param_1="bacon")
        assert processor.param_2 == -25

    def test_unknown_param(self, processor_type):
        with pytest.raises(ValueError):
            processor_type(param_1="bacon", parma_0='monkey')

    def test_abstract_func(self):
        processor = Processor()
        with pytest.raises(NotImplementedError):
            processor(0)

    def test_checkpoint(self, processor_type):
        processor = processor_type(param_1="bacon", is_checkpoint=True)
        out = processor(0)
        assert processor.checkpoint_data == out

    def test_param_values(self, processor_type, kwargs):
        processor = processor_type(**kwargs)
        assert processor.param_values() == kwargs

    def test_copy_param_values(self, processor_type, kwargs):
        processor = processor_type(**kwargs)
        copy = processor.copy()
        assert processor.param_values() == copy.param_values()

    def test_multiple_dtype(self, processor_type):
        processor_type(param_1='soup', param3=21)
        processor_type(param_1='soup', param3='spoon')

    def test_mandatory_param(self, processor_type):
        with pytest.raises(ValueError):
            processor_type()

    def test_wrong_type_param(self, processor_type):
        with pytest.raises(TypeError):
            processor_type(param_1=2)

    def test_bad_dtype(self):
        with pytest.raises(ValueError):
            class TestProcessor1(Processor):
                param = Param(2)
