import pytest

from sprincl.processor.base import Processor, Param, FunctionProcessor, ensure_processor


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


@pytest.fixture(scope='module')
def function():
    def some_function(self, data):
        return 42
    return some_function


@pytest.fixture(scope='module')
def unbound_function():
    def some_function(data):
        return 42
    return some_function


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
        with pytest.raises(TypeError):
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
        processor_type(param_1='soup', param_3=21)
        processor_type(param_1='soup', param_3='spoon')

    def test_mandatory_param(self, processor_type):
        with pytest.raises(TypeError):
            processor_type()

    def test_wrong_type_param(self, processor_type):
        with pytest.raises(TypeError):
            processor_type(param_1=2)

    def test_bad_dtype(self):
        with pytest.raises(TypeError):
            class TestProcessor1(Processor):
                param = Param(2)

    def test_update_defaults(self, processor_type):
        proc = processor_type(param_1='soup')
        proc.update_defaults(param_2=1)
        assert proc.param_2 == 1

    def test_reset_defaults(self, processor_type):
        proc = processor_type(param_1='soup')
        proc.update_defaults(param_2=1)
        proc.reset_defaults()
        assert proc.param_2 == -25

    def test_reset_defaults_assigned(self, processor_type):
        proc = processor_type(param_1='soup', param_2=2)
        proc.update_defaults(param_2=1)
        proc.reset_defaults()
        assert proc.param_2 == 2

    def test_update_defaults_wrong_dtype(self, processor_type):
        proc = processor_type(param_1='soup')
        with pytest.raises(TypeError):
            proc.update_defaults(param_2='bogus')


class TestFunctionProcessor(object):
    def test_instantiation(self, unbound_function):
        FunctionProcessor(function=unbound_function)

    def test_instance_call(self, unbound_function):
        processor = FunctionProcessor(function=unbound_function)
        assert processor(0) == unbound_function(0)

    def test_instance_call_bound(self, function):
        processor = FunctionProcessor(function=function, bind_method=True)
        assert processor(0) == function(processor, 0)

    def test_non_callable(self):
        with pytest.raises(TypeError):
            FunctionProcessor(function='monkey')


class TestEnsureProcessor(object):
    def test_processor(self, processor_type):
        processor = processor_type(param_1='giraffe')
        ensured = ensure_processor(processor)
        assert processor is ensured

    def test_function(self, unbound_function):
        ensured = ensure_processor(unbound_function)
        assert isinstance(ensured, FunctionProcessor)

    def test_invalid(self):
        with pytest.raises(TypeError):
            ensure_processor('mummy')

    def test_default_param_omitted(self, processor_type):
        processor = processor_type(param_1='giraffe')
        ensured = ensure_processor(processor, is_output=True)
        assert ensured.is_output

    def test_default_param_assigned(self, processor_type):
        processor = processor_type(param_1='giraffe', is_output=False)
        ensured = ensure_processor(processor, is_output=True)
        assert not ensured.is_output
