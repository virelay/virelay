from collections import OrderedDict
from types import FunctionType

import pytest

from sprincl.processor.base import Processor, Param, FunctionProcessor
from sprincl.pipeline.base import Pipeline, Task


@pytest.fixture(scope='module')
def processor_type():
    class MyProcessor(Processor):
        param_1 = Param(object)
        param_2 = Param(object)

        def function(self, data):
            return data * 2

    return MyProcessor


@pytest.fixture(scope='module')
def pipeline_type(processor_type):
    class MyPipeline(Pipeline):
        task_1 = Task(FunctionProcessor, lambda x: x + 3, is_output=False)
        task_2 = Task(processor_type, processor_type(), is_output=True)

    return MyPipeline


@pytest.fixture(scope='module')
def pipeline_type_multi(processor_type):
    class MyPipeline(Pipeline):
        task_1 = Task(FunctionProcessor, lambda x: x + 2, is_output=True)
        task_2 = Task(FunctionProcessor, lambda x: x * 2, is_output=True)

    return MyPipeline


class TestTask(object):
    def test_instantiation_default(self):
        Task()

    def test_instantiation_arguments(self, processor_type):
        Task(proc_type=processor_type, default=processor_type(), is_output=True)

    def test_proc_type_no_proc(self):
        with pytest.raises(TypeError):
            Task(proc_type=FunctionType, default=(lambda x: x))

    def test_default_no_proc(self):
        with pytest.raises(TypeError):
            Task(proc_type=object, default='bla')

    def test_proc_type_default_type_mismatch(self, processor_type):
        with pytest.raises(TypeError):
            Task(proc_type=processor_type, default=(lambda x: x))

    def test_default_function_identity(self):
        task = Task()
        assert 42 == task.default(42)

    def test_assigned_default(self, processor_type):
        task = Task(proc_type=processor_type, default=processor_type())
        assert 10 == task.default(5)


class TestPipeline(object):
    def test_instatiation_base(self):
        Pipeline()

    def test_instatiation_default(self, pipeline_type):
        pipeline_type()

    def test_instatiation_arguments(self, pipeline_type, processor_type):
        pipeline_type(task_1=lambda x: x + 2, task_2=processor_type())

    def test_default_call(self, pipeline_type):
        pipeline = pipeline_type()
        pipeline(0)

    def test_default_call_no_input(self, pipeline_type):
        pipeline = pipeline_type()
        with pytest.raises(TypeError):
            pipeline()

    def test_default_call_output(self, pipeline_type):
        pipeline = pipeline_type()
        out = pipeline(1)
        assert out == 8

    def test_default_call_output_multiple(self, pipeline_type_multi):
        pipeline = pipeline_type_multi()
        out = pipeline(0)
        assert out == (2, 4)

    def test_checkpoint_processes(self, pipeline_type, processor_type):
        proc_1 = FunctionProcessor(function=lambda x: x + 5, is_checkpoint=False)
        proc_2 = processor_type(is_checkpoint=True)
        pipeline = pipeline_type(task_1=proc_1, task_2=proc_2)
        assert pipeline.checkpoint_processes() == OrderedDict(task_2=proc_2)

    def test_checkpoint_data(self, pipeline_type, processor_type):
        proc_1 = FunctionProcessor(function=lambda x: x + 5, is_checkpoint=True)
        proc_2 = processor_type(is_checkpoint=False)
        pipeline = pipeline_type(task_1=proc_1, task_2=proc_2)
        pipeline(0)
        assert proc_1.checkpoint_data == 5

    def test_from_checkpoint(self, pipeline_type, processor_type):
        proc_1 = FunctionProcessor(function=lambda x: x + 5, is_checkpoint=True)
        proc_2 = processor_type(is_checkpoint=False)
        pipeline = pipeline_type(task_1=proc_1, task_2=proc_2)
        proc_1.checkpoint_data = 1
        out = pipeline.from_checkpoint()
        assert out == 2
