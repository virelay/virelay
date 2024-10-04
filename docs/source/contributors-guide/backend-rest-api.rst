================
Backend REST API
================

ViRelAy consists of 2 parts: the backend REST API and the frontend website. This article describes the architecture of the backend REST API in detail. The backend REST API is implemented in Python using `Flask <https://flask.palletsprojects.com/en/3.0.x/>`_. It consists of four Python modules:

- **Application** -- The ``application`` module contains the entrypoint to the backend REST API, the command line interface for starting the built-in development server, as well as the ``create_app`` function, which is used by Gunicorn to start the application.
- **Image Processing** -- The ``image_processing`` module contains functions for up and down sampling input images and generated heatmaps from attributions.
- **Model** -- The ``model`` module contains the classes for loading and reading ViRelAy projects, datasets, attribution databases, and analysis databases.
- **Server** -- The ``server`` module contains the server class, which implements the REST API using Flask.

Please refer to the :doc:`../api-reference/index` for detailed information about the modules, their classes, and functions.

We manage the backend REST API project using the Python package and project manager `uv <https://github.com/astral-sh/uv>`_. You can find instructions on how to install and use uv in the `official documentation <https://docs.astral.sh/uv/>`_. This tool is used to install supported Python versions, manage virtual environments, manage runtime and development dependencies, build the project, and run ViRelAy. After installing uv, you first have to install the supported Python versions, which are 3.10, 3.11, 3.12, and 3.13. The versions are listed in the :repo:`.python-versions` file and can be installed using the following command:

.. code-block:: console

    $ uv python install

After installing the supported Python versions, the project's dependencies have to be installed: *H5py* for reading HDF5 datasets, attribution databases and analysis databases, *Matplotlib*, *Pillow* and *NumPy* for manipulating images and rendering heatmaps, *Flask* for the REST API, *Flask CORS* for cross-origin resource sharing (which is required so that the frontend can access the REST API), *Gunicorn* as an HTTP server, *PyYAML* to read ViRelAy project files, *Sphinx* to build the documentation, *PyTest* and *Coverage* for unit testing and measuring code coverage, *PyLint*, *PyCodeStyle*, and *PyDocLint* for linting, *MyPy* for static type checking, *tox* to run tests, run the linters, run the type checker and to build the documentation. All necessary dependencies are included in the :repo`pyproject.toml` project file and specific versions are pinned in the :repo`uv.lock` file. They can be installed using the following command:

.. code-block:: console

    $ uv sync

ViRelAy can then be run using the following command:

.. code-block:: console

    $ uv run virelay '<project-file>' ['<project-file>' ...]

Command Line interface
======================

The ViRelAy command line interface can be used like so:

.. code-block:: console

    $ uv run virelay [-h] [-H HOST] [-p PORT] [-d] project [project ...]

The following arguments are supported:

- ``project`` -- The project file that is to be loaded into the workspace. Multiple project files can be specified.
- ``-h`` / ``--host`` -- The name or IP address at which the server should run. Defaults to "localhost".
- ``-p`` / ``--port`` -- -p PORT, --port PORT  The port at which the server should run. Defaults to 8080.
- ``-d`` / ``--debug-mode`` -- Determines whether the application is run in debug mode. When the application is in debug mode, all Flask and Werkzeug logs are printed to stdout, Flask debugging is activated (Flask will print out the debugger PIN for attaching the debugger), and automatic reloading (when files change) is activated. Furthermore, the frontend of the application will not be served by Flask and instead has to be served externally (e.g. via ng serve).
- ``-h`` / ``--help`` -- Shows a help message and exits.

Especially, the debug mode is an important option for development, because it not only prints out verbose logging messages and allows you to attach a debugger, but it also allows you to run the frontend separately, which enables debugging and hot-reloading of the frontend.

REST API
========

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
============

The backend REST API has a unit test suite which strives to always reach 100% code coverage. The tests are not situated in the ViRelAy module, but in a separate tests directory: :repo:`tests/unit_tests`. The ``conftest`` module contains common fixtures that are used by the tests. Each ViRelAy module has an accompanying test module, which contains the tests for it (e.g., the ``image_processing`` ViRelAy module has a ``test_image_processing`` test module). The tests are written using the `PyTest framework <https://docs.pytest.org/en/stable/>`_. The tests for ViRelAy classes are also contained in classes (e.g., the ``Project`` class in the ``model`` ViRelAy module has a matching ``TestProject`` test class), while the tests for functions are also just plain functions. The convention is to name a test function or method with the prefix ``test_`` followed by the name of the function or method being tested, followed by a description of the test. For example, the function that tests whether heatmaps can be rendered with the blue-white-red color map is called ``test_render_heatmap_blue_white_red``. When contributing to the project, you should always ensure that all tests run successfully and that all altered or added functionality is being properly tested.

The easiest way to run the unit tests is through tox. To run all tox environments, i.e., ``py310``, ``py311``, ``py312``, and  ``py313`` for the unit tests using Python 3.10, 3.11, 3.12, and 3.13, ``coverage`` for combining the test coverage data and producing a report, ``pylint``, ``pycodestyle`` and ``pydoclint`` for running the linters, ``mypy`` for running the static type checker, and ``docs`` for building the documentation, you can just invoke the ``uv run tox --conf tests/config/tox.ini --root .`` command in your terminal without any arguments. To run specific environments, you can use the ``-e`` parameter. For example, to run the unit tests for Python 3.10, and the PyLint linter you can use the following command:

.. code-block:: console

    $ uv run tox --conf tests/config/tox.ini --root . -e py310,pylint

The tests can also be manually executed using the ``pytest`` command line interface, like so:

.. code-block:: console

    $ uv run pytest tests/unit_tests

This will run all tests and report how many tests where successful and how many tests failed. Furthermore, the code coverage needs to be measured in order to make sure that 100% of the code is covered by the unit test suite at all times.

.. code-block:: console

    $ uv run pytest --cov source/virelay --cov-config tests/config/tox.ini tests/unit_tests

The ``--cov`` argument specifies the module against which the code coverage is to be measured and the ``--cov-config`` argument specifies, that the tox configuration file also contains the configuration for the test coverage. This command will then print out test coverage statistics. If you want to have a more elaborate report in the form of an HTML website, then you can add the ``--cov-report html`` argument, like so:

.. code-block:: console

    $ uv run pytest --cov source/virelay --cov-config tests/config/tox.ini --cov-report html tests/unit_tests

The unit tests are run as part continuous integration (CI) pipeline, which we will run when a pull request is created. Pull requests with a failing CI pipeline are not accepted.

Linting
=======

The code style of the backend REST API is checked using `PyLint <https://www.pylint.org/>`_, `PyCodeStyle <https://pycodestyle.pycqa.org/en/latest/intro.html>`_, and `PyDocLint <https://jsh9.github.io/pydoclint/>`_`. They are also used to find some forms of runtime bugs. Furthermore, we use the static type checker `MyPy <https://mypy-lang.org/>`_ to ensure that there are no type errors in the code. Please make sure to run them regularly and fix all produced warnings. Especially, before committing or creating a pull request, you should absolutely make sure that they all run without warning. Linting and static type checking runs as part of the CI pipeline, which we will run when a pull request is created. Pull requests with a failing CI pipeline are not accepted.

The configuration for PyLint can be found in the :repo:`tests/config/.pylintrc` file, the PyCodeStyle configuration can be found in the :repo:`tests/config/.pycodestyle` file, PyDocLint's configuration can be found in the :repo:`tests/config/.pydoclint.toml` file, and the configuration for MyPy can be found in the :repo:`tests/config/.mypy.ini` file.

Again, the easiest way to run all linters and the static type checker is through tox:

.. code-block:: console

    $ uv run tox --conf tests/config/tox.ini --root . -e pylint,pycodestyle,pydoclint,mypy

However, the linters and the type checker can also be directly run, if you have installed them in your virtual environment (``.venv/bin/pip install --editable .[linting]``):

.. code-block:: console

    $ uv run pylint \
        --rcfile tests/config/.pylintrc \
        source/virelay \
        tests/unit_tests \
        docs/source/conf.py

    $ uv run pycodestyle \
        --config tests/config/.pycodestyle \
        source/virelay \
        tests/unit_tests \
        docs/source/conf.py

    $ uv run pydoclint \
        --config tests/config/.pydoclint.toml \
        source/virelay \
        tests/unit_tests \
        docs/source/conf.py

    $ uv run mypy \
        --config-file tests/config/.mypy.ini \
        source/virelay \
        tests/unit_tests \
        docs/source/conf.py

The example scripts in the documentation have dependencies that currently do not support Python 3.10 or later. For this reason they cannot be linted using the project's dependencies. They also require some extra dependencies that would have to be installed separately. For this reason, it is easier to run them using ``uv run`` with the ``--no-project`` flag, which will run the script without the project's dependencies. The ``--python`` and ``--with`` arguments specify the Python version and the dependencies that are to be used for the example scripts.

.. code-block:: console

    $ uv run \
        --no-project \
        --python 3.9.20 \
        --with 'pylint==3.3.1' \
        --with 'zennit==0.5.1' \
        --with 'corelay==0.2.1' \
        --with 'h5py==3.12.1' \
        --with 'pyyaml==6.0.2' \
        pylint \
            --rcfile tests/config/.pylintrc \
            --disable duplicate-code \
            docs/examples/*.py \
            docs/examples/**/*.py

    $ uv run \
        --no-project \
        --python 3.9.20 \
        --with 'pycodestyle==2.12.1' \
        --with 'zennit==0.5.1' \
        --with 'corelay==0.2.1' \
        --with 'h5py==3.12.1' \
        --with 'pyyaml==6.0.2' \
        pycodestyle \
            --config tests/config/.pycodestyle \
            docs/examples/*.py \
            docs/examples/**/*.py

    $ uv run \
        --no-project \
        --python 3.9.20 \
        --with 'pydoclint==0.5.9' \
        --with 'zennit==0.5.1' \
        --with 'corelay==0.2.1' \
        --with 'h5py==3.12.1' \
        --with 'pyyaml==6.0.2' \
        pydoclint \
            --config tests/config/.pydoclint.toml \
            docs/examples/*.py \
            docs/examples/**/*.py

    $ uv run \
        --no-project \
        --python 3.9.20 \
        --with 'mypy==1.12.0' \
        --with 'zennit==0.5.1' \
        --with 'corelay==0.2.1' \
        --with 'h5py==3.12.1' \
        --with 'pyyaml==6.0.2' \
        --with 'types-PyYAML==6.0.12.20240917' \
        mypy \
            --config-file tests/config/.mypy.ini \
            --ignore-missing-imports \
            docs/examples/*.py \
            docs/examples/**/*.py
