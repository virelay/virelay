================
Backend REST API
================

ViRelAy consists of 2 parts: the backend REST API and the frontend website. This article describes the architecture of the backend REST API in detail. The backend REST API is implemented in Python using `Flask <https://flask.palletsprojects.com/en/2.1.x/>`_. It consists of four Python modules:

- **Application** -- The ``application`` module contains the entrypoint to the backend REST API, the command line interface for starting the built-in development server, as well as the ``create_app`` function, which is used by Gunicorn to start the application.
- **Image Processing** -- The ``image_processing`` module contains functions for up and down sampling input images and generated heatmaps from attributions.
- **Model** -- The ``model`` module contains the classes for loading and reading ViRelAy projects, datasets, attribution databases, and analysis databases.
- **Server** -- The ``server`` module contains the server class, which implements the REST API using Flask.

Please refer to the :doc:`../api-reference/index` for detailed information about the modules, their classes, and functions.

When working on the backend REST API, it is recommended that you create a virtual environment, in order not to clutter your base environment. The following dependencies are required: *H5py* for reading HDF5 datasets, attribution databases and analysis databases, *Matplotlib*, *Pillow* and *NumPy* for manipulating images and rendering heatmaps, *Flask* for the REST API, *Flask CORS* for cross-origin resource sharing (which is required so that the frontend can access the REST API), *PyYAML* to read ViRelAy project files, and *tox* to run tests, run the linters and to build the documentation. All necessary dependencies, except for *tox*, are installed when you install ViRelAy. There are three sets of extra dependencies that can be installed: ``docs`` for building the documentation, ``tests`` for running the unit tests, and ``linting`` for running the linters. All of these can be run through ``tox``, so you only need to install them if you want to directly use them from the terminal. You can clone the repository, create a virtual environment, and install everything necessary by issuing the following commands in your terminal:

.. code-block:: console

    $ git clone https://github.com/virelay/virelay.git
    $ cd virelay
    $ python -m venv .venv
    $ .venv/bin/pip install --editable .                     # Install ViRelAy, or
    $ .venv/bin/pip install --editable .[docs,tests,linting] # install ViRelAy with optional extra dependencies
    $ .venv/bin/pip install tox

The backend REST API server can then be run using the following command:

.. code-block:: console

    $ .venv/bin/python -m virelay '<project-file>' ['<project-file>' ...]

Command Line interface
----------------------

The ViRelAy command line interface can be used like so:

.. code-block:: console

    $ .venv/bin/python -m virelay [-h] [-H HOST] [-p PORT] [-d] project [project ...]

The following arguments are supported:

- ``project`` -- The project file that is to be loaded into the workspace. Multiple project files can be specified.
- ``-h`` / ``--host`` -- The name or IP address at which the server should run. Defaults to "localhost".
- ``-p`` / ``--port`` -- -p PORT, --port PORT  The port at which the server should run. Defaults to 8080.
- ``-d`` / ``--debug-mode`` -- Determines whether the application is run in debug mode. When the application is in debug mode, all Flask and Werkzeug logs are printed to stdout, Flask debugging is activated (Flask will print out the debugger PIN for attaching the debugger), and automatic reloading (when files change) is activated. Furthermore, the frontend of the application will not be served by Flask and instead has to be served externally (e.g. via ng serve).
- ``-h`` / ``--help`` -- Shows a help message and exits.

Especially, the debug mode is an important option for development, because it not only prints out verbose logging messages and allows you to attach a debugger, but it also allows you to run the frontend separately, which enables debugging and hot-reloading of the frontend.

REST API
--------

The ViRelAy backend REST API supports the following endpoints:

- ``/api/projects`` -- Retrieves all the projects and their respective information from the workspace. Returns an HTTP 200 OK response with a JSON string as content that contains the projects of the workspace as well as their information.
- ``/api/projects/<int:project_id>`` -- Retrieves the project with the specified ID. Returns an HTTP 200 OK response with a JSON string as content, which contains the project information. If the specified project could not be found, then an HTTP 404 Not Found response is returned.
- ``/api/projects/<int:project_id>/dataset/<int:sample_index>`` -- Retrieves the dataset sample with the specified index from the specified project. Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the dataset sample. If the specified project does not exist, then an HTTP 404 Not Found response is returned. If the specified dataset sample does not exist, then an HTTP 404 Not Found response is returned.
- ``/api/projects/<int:project_id>/dataset/<int:sample_index>/image`` -- Retrieves the image of the dataset with the specified index from the specified project. Returns an HTTP 200 OK response with the image of the specified dataset sample as content. If the specified project does not exist, then an HTTP 404 Not Found response is returned. If the specified dataset sample does not exist, then an HTTP 404 Not Found response is returned.
- ``/api/projects/<int:project_id>/attributions/<int:attribution_index>?imageMode=<string:image_mode>`` -- Retrieves the attribution with the specified index from the specified project. The image mode can either be "input", "overlay", or "attribution", defaults to "input". Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the attribution. If the specified project does not exist, then an HTTP 404 Not Found response is returned. If the specified attribution does not exist, then an HTTP 404 Not Found response is returned.
- ``/api/projects/<int:project_id>/attributions/<int:attribution_index>/heatmap?colorMap=<string:color_map>&superimpose=<bool:superimpose>`` -- Renders a heatmap from the attribution with the specified index from the specified project. The color map can be one of: "gray-red", "black-green", "black-fire-red", "black-yellow", "blue-white-red", "afm-hot", "jet", or "seismic", defaults to "black-fire-red". Superimpose can be either "true" or "false", defaults to "false". Returns an HTTP 200 OK response with the rendered heatmap image. If the specified project does not exist, then an HTTP 404 Not Found response is returned. If the specified attribution does not exist, then an HTTP 404 Not Found response is returned.
- ``/api/projects/<int:project_id>/analyses/<string:analysis_method_name>?category=<string:category>&clustering=<string:clustering>&embedding=<string:embedding>`` -- Retrieves the analysis from the specified project with the specified analysis method. Besides the project ID and the analysis method name, the name of the category, clustering, and embedding have to be specified as URL parameters. Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the analysis. If the specified project does not exist, then an HTTP 404 Not Found response is returned. If the specified analysis method does not exist, then an HTTP 404 Not Found response is returned. If the analysis does not exist, then an HTTP 404 Not Found response is returned. If no category name, clustering name, or embedding name were specified in the URL parameters, then an HTTP 400 Bad Request response is returned.
- ``/api/color-maps`` -- Retrieves the names of all the color maps that are supported. Returns an HTTP 200 OK response with a JSON list of all the supported color maps as content.
- ``/api/color-maps/<string:color_map>?width=<int:width>&height=<int:height>`` -- Renders a preview of a color map with a value gradient. Using the URL parameters "width" and "height", the size of the preview can be specified. The size defaults to 200x20. Returns an HTTP 200 OK response with the rendered heatmap preview. If the specified color map is unknown, then an HTTP 400 Bad Request response is returned.

Furthermore, if the backend REST API server is not run in debug mode, then the frontend is also served via the backend server. This makes running ViRelAy much easier, because no separate HTTP server is required. The frontend is served via the following endpoints:

- ``/`` -- Serves the index page of the frontend.
- ``/favicon.ico`` -- Serves the favicon of the frontend.
- ``/<string:file_name>.css`` -- Serves a CSS style sheet. If the style sheet file could not be found, then an HTTP 404 Not Found response is returned.
- ``/<string:file_name>.js`` -- Serves a JavaScript file. If the JavaScript file could not be found, then an HTTP 404 Not Found response is returned.
- ``/assets/images/<string:file_name>.png`` Serves an image file. If the image file could not be found, then an HTTP 404 Not Found response is returned.
- ``/<path:file_name>`` -- A catch all for all other paths, which also serves the index page of the frontend.

Unit Testing
------------

The backend REST API has a unit test suite which strives to always reach 100% code coverage. The tests are not situated in the ViRelAy module, but in a separate tests directory: :repo:`tests/unit_tests`. The ``conftest`` module contains common fixtures that are used by the tests. Each ViRelAy module has an accompanying test module, which contains the tests for it (e.g., the ``image_processing`` ViRelAy module has a ``test_image_processing`` test module). The tests are written using the PyTest framework. The tests for ViRelAy classes are also contained in classes (e.g., the ``Project`` class in the ``model`` ViRelAy module has a matching ``TestProject`` test class), while the tests for functions are also just plain functions. The convention is to name a test function or method with the prefix ``test_`` followed by the name of the function or method being tested, followed by a description of the test. For example, the function that tests whether heatmaps can be rendered with the blue-white-red color map is called ``test_render_heatmap_blue_white_red``. When contributing to the project, you should always ensure that all tests run successfully and that all altered or added functionality is being properly tested.

The easiest way to run the unit tests is through tox. To run all tox environments, i.e., ``py310``, ``py311`` and ``py312`` for the unit tests using Python 3.10, 3.11 and 3.12, ``coverage`` for computing the test coverage, ``linting`` for running the linters and the static type checker, and ``docs`` for building the documentation, you can just invoke the ``tox`` command in your terminal without any arguments. To run specific environments, you can use the ``-e`` parameter. For example, to run the unit tests for Python 3.10, and the linters and static type checker you can use the following command:

.. code-block:: console

    tox -e py310,linting

Using tox, the unit tests can be run with all supported Python versions. For this to work, all supported Python versions, i.e., Python 3.10, 3.11 and 3.12, must be installed on your system. If you cannot or do not want to install all supported Python versions on your system, you can also run tox in Docker. For this to work, you need to have Docker installed on your system, which can be achieved by following the `official installation instructions <https://docs.docker.com/engine/install/>`_. Then you can run tox inside of Docker using our bundled convenience script:

.. code-block:: console

    ./tests/docker-tox/docker-tox

The script will automatically build a Docker image with all necessary dependencies, if it is not already locally available, and then run tox inside of a Docker container using the built image. The convenience script will pass all command line arguments unaltered to tox, which means it can be used as a drop-in replacement for a locally installed tox. Additional arguments can be passed to the script like so:

.. code-block:: console

    ./tests/docker-tox/docker-tox -e py310,linting

The tests can also be manually executed using the ``pytest`` command line interface, like so:

.. code-block:: console

    $ .venv/bin/python -m pytest tests/unit_tests

This will run all tests and report how many tests where successful and how many tests failed. Furthermore, the code coverage needs to be measured in order to make sure that 100% of the code is covered by the unit test suite at all times.

.. code-block:: console

    .venv/bin/python -m pytest --cov virelay --cov-config tox.ini tests/unit_tests

The ``--cov`` argument specifies the module against which the code coverage is to be measured and the ``--cov-config`` argument specifies, that the tox configuration file also contains the configuration for the test coverage. This command will then print out test coverage statistics. If you want to have a more elaborate report in the form of an HTML website, then you can add the ``--cov-report html`` argument, like so:

.. code-block:: console

    .venv/bin/python -m pytest --cov virelay --cov-config tox.ini --cov-report html tests/unit_tests

The unit tests are run as part continuous integration (CI) pipeline, which we will run when a pull request is created. Pull requests with a failing CI pipeline are not accepted.

Linting
-------

The code style of the backend REST API is checked using `PyLint <https://www.pylint.org/>`_, `PyCodeStyle <https://pycodestyle.pycqa.org/en/latest/intro.html>`_, and `PyDocLint <https://jsh9.github.io/pydoclint/>`_`. They are also used to find some forms of runtime bugs. Furthermore, we use the static type checker `MyPy <https://mypy-lang.org/>`_ to ensure that there are no type errors in the code. Please make sure to run them regularly and fix all produced warnings. Especially, before committing or creating a pull request, you should absolutely make sure that they all run without warning. Linting and static type checking runs as part of the CI pipeline, which we will run when a pull request is created. Pull requests with a failing CI pipeline are not accepted.

The configuration for PyLint can be found in the :repo:`.pylintrc` file, the PyCodeStyle configuration can be found in the :repo:`.pycodestyle` file, PyDocLint's configuration can be found in the :repo:`.pydoclint.toml` file, and the configuration for MyPy can be found in the :repo:`.mypy.ini` file.

Again, the easiest way to execute the linting is through tox:

.. code-block:: console

    tox -e linting

Of course, the same can be achieved using tox in Docker:

.. code-block:: console

    ./tests/docker-tox/docker-tox -e linting

However, the linters and the type checker can also be directly run, if you have installed them in your virtual environment (``.venv/bin/pip install --editable .[linting]``):

.. code-block:: console

    pylint --rcfile .pylintrc virelay tests/unit_tests setup.py docs/source/conf.py
    pycodestyle --config .pycodestyle virelay tests/unit_tests setup.py docs/source/conf.py
    pydoclint --config .pydoclint.toml virelay tests/unit_tests setup.py docs/source/conf.py
    mypy --config-file .mypy.ini virelay tests/unit_tests setup.py docs/source/conf.py
