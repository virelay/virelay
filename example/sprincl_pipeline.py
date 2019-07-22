import numpy as np

from sprincl.pipeline.base import Pipeline, Task
from sprincl.processor.base import Processor, Param, FunctionProcessor
from sprincl.processor.affinity import Affinity, RadialBasisFunction
from sprincl.processor.distance import Distance, SciPyPDist


# Processors
class MyProcess(Processor):
    # Parameters are registerd by defining a class attribute of type Param, and will be set in __init__ automatically,
    # which expects keyword arguments with the same name
    # the first value is a type specification, the second a default value
    stuff = Param(dtype=int, default=2)
    func = Param(callable, lambda x: x**2)

    # Parameters can be accessed as self.<parameter-name>
    def function(self, data):
        return self.stuff * self.func(data) + 3


# Pipelines
class MyPipeline(Pipeline):
    # Task are registered in order by creating a class attribute of type Task() and, like params, are expected to
    # supplied with the same name in __init__ as a keyword argument
    # first value is an optional expected Process type, second is a default value, which has to be an instance of that
    # type
    # if the default argument is not a Process, it will be converted to a FunctionProcessor
    preprocess = Task(proc_type=FunctionProcessor, default=(lambda x: x**2))
    pdistance = Task(Distance, SciPyPDist(metric='sqeuclidean'))
    affinity = Task(Affinity, RadialBasisFunction(sigma=1.0))
    postprocess = Task()


# Tasks are filled with Processes during initialization of the Pipeline class
# keyword arguments do not have to be in order, and if not supplied, the default value will be used
pipeline = MyPipeline(
    preprocess=(lambda x: x.mean(1)),
    affinity=RadialBasisFunction(sigma=.1),
    postprocess=MyProcess(stuff=3)
)
output = pipeline(np.ones((5, 3, 5)))
print(output)
