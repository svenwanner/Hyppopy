&emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; ![docs_title_logo](./resources/docs_title_logo.png)
# A Hyper-Parameter Optimization Toolbox
<br>

_Acknowledgements: This work is supported by the [Helmholtz Association Initiative and Networking](https://www.helmholtz.de/en/about_us/the_association/initiating_and_networking/) Fund under project number ZT-I-0003._
<br>

## What is Hyppopy?

Hyppopy is a python toolbox for blackbox optimization. It's purpose is to offer a unified and easy to use interface to a collection of solver libraries. Currently provided solvers are:

* [Hyperopt](http://hyperopt.github.io/hyperopt/)
* [Optunity](https://optunity.readthedocs.io/en/latest/user/index.html)
* [Optuna](https://optuna.org/)
* [BayesianOptimization](https://github.com/fmfn/BayesianOptimization)
* Randomsearch Solver
* Gridsearch Solver

## Installation

1. clone the [Hyppopy](http:\\github.com) project from Github
2. (create a virtual environment), open a console (with your activated virtual env) and go to the hyppopy root folder
3. ```$ pip install -r requirements.txt```
4. ```$ python setup.py install```


## How to use Hyppopy?

#### The HyppopyProject class

The HyppopyProject class takes care all settings necessary for the solver and your workflow. To setup a HyppopyProject instance we can use a nested dictionary or the classes memberfunctions respectively.

```python
# Import the HyppopyProject class
from hyppopy.HyppopyProject import HyppopyProject

# Create a nested dict with a section hyperparameter. We define a 2 dimensional
# hyperparameter space with a numerical dimension named myNumber of type float and
# a uniform sampling. The second dimension is a categorical parameter of type string.
config = {
"hyperparameter": {
    "myNumber": {
        "domain": "uniform",
        "data": [0, 100],
        "type": "float"
    },
    "myOption": {
        "domain": "categorical",
        "data": ["a", "b", "c"],
        "type": "str"
    }
}}

# Create a HyppopyProject instance and pass the config dict to
# the constructor. Alternatively one can use set_config method.
project = HyppopyProject(config=config)

# To demonstrate the second option we clear the project
project.clear()

# and add the parameter again using the member function add_hyperparameter
project.add_hyperparameter(name="myNumber", domain="uniform", data=[0, 100], dtype="float")
project.add_hyperparameter(name="myOption", domain="categorical", data=["a", "b", "c"], dtype="str")
```

```python
from hyppopy.HyppopyProject import HyppopyProject

# We might have seen a warning: 'UserWarning: config dict had no
# section settings/solver/max_iterations, set default value: 500'
# when executing the example above. This is due to the fact that
# most solvers need a value for a maximum number of iterations.
# To take care of solver settings (there might be more in the future)
# one can set a second section called settings. The settings section
# again is splitted into a subsection 'solver' and a subsection 'custom'.
# When adding max_iterations to the section settings/solver we can change
# the number of iterations the solver is doing. All solver except of the
# GridsearchSolver make use of the value max_iterations.
# The usage of the custom section is demonstrated later.
config = {
"hyperparameter": {
    "myNumber": {
        "domain": "uniform",
        "data": [0, 100],
        "type": "float"
    },
    "myOption": {
        "domain": "categorical",
        "data": ["a", "b", "c"],
        "type": "str"
    }
},
"settings": {
    "solver": {
        "max_iterations": 500
    },
    "custom": {}
}}
project = HyppopyProject(config=config)
```

The settings added are automatically converted to a class member with a prefix_ where prefix is the name of the subsection. One can make use of this feature to build custom workflows by adding params to the custom section. More interesting is this feature when developing your own solver.

```python
from hyppopy.HyppopyProject import HyppopyProject

# Creating a HyppopyProject instance
project = HyppopyProject()
project.add_hyperparameter(name="x", domain="uniform", data=[-10, 10], dtype="float")
project.add_hyperparameter(name="y", domain="uniform", data=[-10, 10], dtype="float")
project.add_settings(section="solver", name="max_iterations", value=300)
project.add_settings(section="custom", name="my_param1", value=True)
project.add_settings(section="custom", name="my_param2", value=42)

print("What is max_iterations value? {}".format(project.solver_max_iterations))
if project.custom_my_param1:
	print("What is the answer? {}".format(project.custom_my_param2))
else:
	print("What is the answer? x")
```

#### The HyppopySolver classes

Each solver is a child of the HyppopySolver class. This is only interesting if you're planning to write a new solver, we will discuss this in the section Solver Development. All solvers we can use to optimize our blackbox function are part of the module 'hyppopy.solver'. Below is a list of all solvers available along with their access key in squared brackets.

* HyperoptSolver [hyperopt]
* OptunitySolver [optunity]
* OptunaSolver [optuna]
* BayesOptSolver [bayesopt]
* RandomsearchSolver [randomsearch]
* GridsearchSolver [gridsearch]

There are two options to get a solver, we can import directly from the hyppopy.solver package or we use the SolverPool class. We look into both options by optimizing a simple function, starting with the direct import case.

```python
# Import the HyppopyProject class
from hyppopy.HyppopyProject import HyppopyProject

# Import the HyperoptSolver class, in this case wh use Hyperopt
from hyppopy.solvers.HyperoptSolver import HyperoptSolver

# Our function to optimize
def my_loss_func(x, y):
    return x**2+y**2

# Creating a HyppopyProject instance
project = HyppopyProject()
project.add_hyperparameter(name="x", domain="uniform", data=[-10, 10], dtype="float")
project.add_hyperparameter(name="y", domain="uniform", data=[-10, 10], dtype="float")
project.add_settings(section="solver", name="max_iterations", value=300)

# create a solver instance
solver = HyperoptSolver(project)
# pass the loss function to the solver
solver.blackbox = my_loss_func
# run the solver
solver.run()

df, best = solver.get_results()

print("\n")
print("*"*100)
print("Best Parameter Set:\n{}".format(best))
print("*"*100)
```

The SolverPool is a class keeping track of all solver classes. We have several options to ask the SolverPool for the desired solver. We can add an option called use_solver to our settings/custom section or to the project instance respectively, or we can use the solver access key (see solver listing above) to ask for the solver directly.

```python
# import the SolverPool class
from hyppopy.SolverPool import SolverPool

# Import the HyppopyProject class
from hyppopy.HyppopyProject import HyppopyProject

# Our function to optimize
def my_loss_func(x, y):
    return x**2+y**2

# Creating a HyppopyProject instance
project = HyppopyProject()
project.add_hyperparameter(name="x", domain="uniform", data=[-10, 10], dtype="float")
project.add_hyperparameter(name="y", domain="uniform", data=[-10, 10], dtype="float")
project.add_settings(section="solver", name="max_iterations", value=300)
project.add_settings(section="custom", name="use_solver", value="hyperopt")

# create a solver instance. The SolverPool class is a singleton
# and can be used without instanciating. It looks in the project
# instance for the use_solver option and returns the correct solver.
solver = SolverPool.get(project=project)
# Another option without the usage of the use_solver field would be:
# solver = SolverPool.get(solver_name='hyperopt', project=project)

# pass the loss function to the solver
solver.blackbox = my_loss_func
# run the solver
solver.run()

df, best = solver.get_results()

print("\n")
print("*"*100)
print("Best Parameter Set:\n{}".format(best))
print("*"*100)
```

#### The BlackboxFunction class
To extend the possibilities beyond using parameter only loss function as in the examples above, the BlackboxFunction class can be used. This class is a wrapper class around the actual loss_function providing a more advanced access to data handling and a callback_function for accessing the solvers iteration loop.
```python
# import the HyppopyProject class keeping track of inputs
from hyppopy.HyppopyProject import HyppopyProject

# import the SolverPool singleton class
from hyppopy.SolverPool import SolverPool

# import the Blackboxfunction class wrapping your problem for Hyppopy
from hyppopy.BlackboxFunction import BlackboxFunction

# Create the HyppopyProject class instance
project = HyppopyProject()
project.add_hyperparameter(name="C", domain="uniform", data=[0.0001, 20], dtype="float")
project.add_hyperparameter(name="gamma", domain="uniform", data=[0.0001, 20], dtype="float")
project.add_hyperparameter(name="kernel", domain="categorical", data=["linear", "sigmoid", "poly", "rbf"], dtype="str")
project.add_settings(section="solver", name="max_iterations", value=500)
project.add_settings(section="custom", name="use_solver", value="optunity")


# The BlackboxFunction signature is as follows:
# BlackboxFunction(blackbox_func=None,
#                  dataloader_func=None,
#                  preprocess_func=None,
#                  callback_func=None,
#                  data=None,
#                  **kwargs)
#
# - blackbox_func: a function pointer to the users loss function
# - dataloader_func: a function pointer for handling dataloading. The function is called once before
#                    optimizing. What it returns is passed as first argument to your loss functions
#                    data argument.
# - preprocess_func: a function pointer for data preprocessing. The function is called once before
#                    optimizing and gets via kwargs['data'] the raw data object set directly or returned
#                    from dataloader_func. What this function returns is then what is passed as first
#                    argument to your loss function.
# - callback_func: a function pointer called after each iteration. The input kwargs is a dictionary
#                  keeping the parameters used in this iteration, the 'iteration' index, the 'loss'
#                  and the 'status'. The function in this example is used for realtime printing it's
#                  input but can also be used for realtime visualization.
# - data: if not done via dataloader_func one can set a raw_data object directly
# - kwargs: dict that whose content is passed to all functions above.

from sklearn.svm import SVC
from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score


def my_dataloader_function(**kwargs):
    print("Dataloading...")
    # kwargs['params'] allows accessing additional parameter passed, 
    # see below my_preproc_param, my_dataloader_input.
    print("my loading argument: {}".format(kwargs['params']['my_dataloader_input']))
    iris_data = load_iris()
    return [iris_data.data, iris_data.target]


def my_preprocess_function(**kwargs):
    print("Preprocessing...")
    # kwargs['data'] allows accessing the input data
    print("data:", kwargs['data'][0].shape, kwargs['data'][1].shape)
    # kwargs['params'] allows accessing additional parameter passed,
    # see below my_preproc_param, my_dataloader_input.
    print("kwargs['params']['my_preproc_param']={}".format(kwargs['params']['my_preproc_param']), "\n")
    # if the preprocessing function returns something,
    # the input data will be replaced with the data returned by this function.
    x = kwargs['data'][0]
    y = kwargs['data'][1]
    for i in range(x.shape[0]):
        x[i, :] += kwargs['params']['my_preproc_param']
    return [x, y]


def my_callback_function(**kwargs):
    print("\r{}".format(kwargs), end="")


def my_loss_function(data, params):
    clf = SVC(**params)
    return -cross_val_score(estimator=clf, X=data[0], y=data[1], cv=3).mean()


# We now create the BlackboxFunction object and pass all function pointers defined above,
# as well as 2 dummy parameter (my_preproc_param, my_dataloader_input) for demonstration purposes.
blackbox = BlackboxFunction(blackbox_func=my_loss_function,
                            dataloader_func=my_dataloader_function,
                            preprocess_func=my_preprocess_function,
                            callback_func=my_callback_function,
                            my_preproc_param=1,
                            my_dataloader_input='could/be/a/path')


# Get the solver
solver = SolverPool.get(project=project)
# Give the solver your blackbox
solver.blackbox = blackbox
# Run the solver
solver.run()
# Get your results
df, best = solver.get_results()

print("\n")
print("*"*100)
print("Best Parameter Set:\n{}".format(best))
print("*"*100)
```

#### The Parameter Space Domains

Each hyperparameter needs a range and a domain specifier. The range, specified via 'data', is the left and right bound of an interval (!!!exception is the domain 'categorical', here 'data' is the actual list of data elements!!!) and the domain specifier the way this interval is sampled. Currently supported domains are:

* uniform (samples the interval [a,b] evenly)
* normal (a gaussian sampling of the interval [a,b] such that mu=a+(b-a)/2 and sigma=(b-a)/6)
* loguniform (a logaritmic sampling of the iterval [a,b], such that the exponent e^x is sampled evenly x=[log(a),log(b)])
* categorical (in this case data is not interpreted as interval but as actual list of objects)

One exception is the GridsearchSolver, here we need to specifiy an interval and a number of samples like so: 'data': [a,b,N]. The max_iterations parameter is obsolet in this case because each axis specifies an individual number of samples.

```python
# import the SolverPool class
from hyppopy.solvers.GridsearchSolver import GridsearchSolver

# Import the HyppopyProject class
from hyppopy.HyppopyProject import HyppopyProject

# Our function to optimize
def my_loss_func(x, y):
    return x**2+y**2

# Creating a HyppopyProject instance
project = HyppopyProject()
project.add_hyperparameter(name="x", domain="uniform", data=[-1.1, 1, 10], dtype="float")
project.add_hyperparameter(name="y", domain="uniform", data=[-1.1, 1, 12], dtype="float")

solver = GridsearchSolver(project=project)

# pass the loss function to the solver
solver.blackbox = my_loss_func
# run the solver
solver.run()

df, best = solver.get_results()

print("\n")
print("*"*100)
print("Best Parameter Set:\n{}".format(best))
print("*"*100)
```

#### Using a Visdom Server to Visualize the Optimization Process

We can simply create a realtime visualization using a visdom server. If installed, start your visdom server via console command:
```
>visdom
```

Go to your browser and open the site: http://localhost:8097

To enable the visualization call the function 'start_viewer' before running the solver:

```python
#enable visualization
solver.start_viewer()
# Run the solver
solver.run()
```

You can also change the port and the server name in start_viewer(port=8097, server="http://localhost")

