import numpy as np

from sprincl.pipeline.base import Pipeline, Task
from sprincl.processor.base import Processor, Param, FunctionProcessor
from sprincl.processor.affinity import Affinity, RadialBasisFunction
from sprincl.processor.distance import Distance, SciPyPDist
from types import FunctionType


# Processors
class MyProcess(Processor):
    # Parameters are registered by defining a class attribute of type Param, and will be set in __init__ automatically,
    # which expects keyword arguments with the same name the first value is a type specification, the second a default
    # value
    stuff = Param(dtype=int, default=2)
    # as class methods have to be bound explicitly, func here acts like a static function of MyProcess to bind it, see
    # :obj:`sprincl.processor.base.FunctionProcessor`
    func = Param(FunctionType, lambda x: x**2)

    # Parameters can be accessed as self.<parameter-name>
    def function(self, data):
        return self.stuff * self.func(data) + 3


# Pipelines
class MyPipeline(Pipeline):
    # Task are registered in order by creating a class attribute of type Task() and, like params, are expected to be
    # supplied with the same name in __init__ as a keyword argument. The first value is an optional expected Process
    # type, second is a default value, which has to be an instance of that type. If the default argument is not a
    # Process, it will be converted to a FunctionProcessor by default, functions fed to FunctionProcessors are by
    # default bound to the class, so we need to supply `self`:
    prepreprocess = Task(proc_type=FunctionProcessor, default=(lambda self, x: x * 2))
    # We can make the FunctionProcessor not bind the function to itself by supplying either a function with extra Task
    # kwarg:
    preprocess = Task(proc_type=FunctionProcessor, default=(lambda x: x**2), bind_method=False)
    # Or we could supply a FunctionProcessor with parameter `bind_method=False`, but note that this way when we supply
    # a function in the pipeline processor, it will default to being bound.
    # >>> preprocess = Task(proc_type=FunctionProcessor, default=FunctionProcessor(function=lambda x: x**2,
    #                                                                              bind_method=False))
    # The code for this check can be found in `sprincl.processor.base.ensure_processor`
    pdistance = Task(Distance, SciPyPDist(metric='sqeuclidean'))
    affinity = Task(Affinity, RadialBasisFunction(sigma=1.0))
    # empty task, does nothing (except return input) by default
    postprocess = Task()


# Use Pipeline 'as is'
pipeline = MyPipeline()
output1 = pipeline(np.random.rand(5, 3))
print('Pipeline output:', output1)

# Tasks are filled with Processes during initialization of the Pipeline class
# keyword arguments do not have to be in order, and if not supplied, the default value will be used
custom_pipeline = MyPipeline(
    # prepreprocess defaults to binding the function to the processor, hence we need to supply `self`
    # >>> prepreprocess=(lambda self, x: x + 1),
    # if we do not need `self`, we can supply our own FunctionProcessor object instead of a function:
    prepreprocess=FunctionProcessor(function=(lambda x: x + 1), bind_method=False),
    # preprocess here cannot be changed to use `bind_method=True`, since we enforced in the pipeline `bind_method=False`
    preprocess=(lambda x: x.mean(1)),
    affinity=RadialBasisFunction(sigma=.1),
    postprocess=MyProcess(stuff=3)
)
output2 = custom_pipeline(np.ones((5, 3, 5)))
print('Custom pipeline output:', output2)
