=============================
Backend REST API Architecture
=============================

The ViRelAy application is built around two core components: a backend REST API and a frontend web app. This section delves into the detailed architecture of the backend REST API.

The backend REST API is implemented in Python utilizing the `Flask <https://flask.palletsprojects.com/en/stable/>`_ web framework. It comprises four distinct modules, each serving a unique purpose:

* **Application Module** -- This module serves as the entrypoint for the backend REST API and contains the command-line interface for launching the built-in server and initializing application execution via `Gunicorn <https://gunicorn.org/>`_ using the ``run_wsgi_app`` function.
* **Image Processing Module** -- Functions for image resizing (up-sampling, down-sampling), as well as heatmap generation from attribution data, are encapsulated within this module.
* **Model Module** -- This module houses classes required for loading and interacting with ViRelAy projects, datasets, attribution databases, and analysis databases.
* **Server Module** -- The server class, which leverages Flask to implement the REST API, is defined in this module.

To gain a thorough comprehension of the modules' constituent elements, including classes, functions, and behavior patterns, please refer to our comprehensive :doc:`../api-reference/index` documentation for detailed insights.

Managing the Backend REST API Project
=====================================

The backend REST API project leverages `uv <https://github.com/astral-sh/uv>`_, a Python package and project manager, to streamline its development lifecycle. For detailed instructions on installing and utilizing uv, please refer to its `comprehensive documentation <https://docs.astral.sh/uv/>`_. This tool enables the efficient installation of supported Python versions, management of virtual environments, handling of runtime and development dependencies, project building, and the execution ViRelAy.

Following the installation of uv, proceed to install the supported Python versions, which comprise 3.10, 3.11, 3.12, and 3.13, as specified in the :repo:`source/backend/.python-versions` file. This can be accomplished via the following command:

.. code-block:: console

    $ uv --directory source/backend python install

Upon installing the supported Python versions, dependencies must be installed via the ``uv sync`` command. These dependencies encompass:

* **H5py** for reading HDF5 datasets, attribution databases, and analysis databases
* **Matplotlib**, **Pillow**, and **NumPy** for image manipulation and heatmap rendering
* **Flask** for REST API implementation
* **Flask CORS** for facilitating cross-origin resource sharing (CORS) between the frontend and backend
* **Gunicorn** as the HTTP server
* **PyYAML** for parsing ViRelAy project files
* **Sphinx** for generating documentation
* **PyTest** and **Coverage**  for unit testing and code coverage measurement
* **PyLint**, **PyCodeStyle**, and **PyDocLint** for linting purposes
* **MyPy** for static type checking
* **tox** for executing tests, linters, the type checker, and building documentation

To leverage ViRelAy's backend functionality, ensure you have all required dependencies in place. These are specified within the :repo:`source/backend/pyproject.toml` project configuration file and constrained to specific versions in the :repo:`source/backend/uv.lock` lock file. To install these dependencies, execute the following command:

.. code-block:: console

    $ uv --directory source/backend sync

To run ViRelAy, use the following command, providing the necessary project files as arguments:

.. code-block:: console

    $ uv --directory source/backend run virelay '<project-file>' ['<project-file>' ...]

Command Line Interface
======================

The ViRelAy command line interface offers a convenient way to start the application. The basic syntax for running the CLI is as follows:

.. code-block:: console

    $ uv --directory source/backend run virelay [-h] [-v] [-d] [-H HOST] [-p PORT] project [project ...]

The CLI accepts several optional arguments to customize the execution environment:

* ``-h`` / ``--help`` -- Displays a help message and terminates.
* ``-v`` / ``--version`` -- Outputs the ViRelAy version and terminates.
* ``-d`` / ``--debug-mode`` -- Enables debug mode, which includes verbose logging, the possibility to attach a debugger (Flask will print out the debugger PIN for attaching the debugger), and automatic reloading of changes. In this mode, Flask will not serve the frontend, requiring it to be served manually.
* ``-H`` / ``--host`` -- Specifies the host name or IP address where the server should run. Defaults to ``localhost``.
* ``-p`` / ``--port`` -- Sets the port number for the server to listen on. Defaults to 8000.
* ``project`` -- Specifies one or more project files to be loaded into the workspace.

When operating in debug mode, the frontend must be served separately using a command like:

.. code-block:: console

    $ npm --prefix source/frontend run start

This also enables you to benefit from the debugging and hot-reloading capabilities of the `Angular CLI <https://angular.dev/cli>`_.

REST API
========

The ViRelAy backend REST API provides the following endpoints to facilitate data retrieval:

* ``GET /api/projects`` -- Retrieves a list of all projects within the workspace, including their ID, name, model, and dataset. Returns an HTTP 200 OK response with a JSON string as content that contains the projects.
* ``GET /api/projects/<int:project_id>`` -- Returns detailed information for a specific project, including its ID, name, model, dataset, and list of analysis methods. Returns an HTTP 200 OK response with a JSON string as content, which contains the project information. If the specified project could not be found, an HTTP 404 Not Found response is returned.
* ``GET /api/projects/<int:project_id>/dataset/<int:sample_index>`` -- Fetches the information of the specified dataset sample within the specified project. Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the dataset sample, including its index, width, height, URL, and list of labels. If the specified project or dataset sample does not exist, an HTTP 404 Not Found response is returned.
* ``GET /api/projects/<int:project_id>/dataset/<int:sample_index>/image`` -- Retrieves the image of the dataset sample with the specified index from the specified project. Returns an HTTP 200 OK response with the image of the specified dataset sample as content. If the specified project or dataset sample does not exist, an HTTP 404 Not Found response is returned.
* ``GET /api/projects/<int:project_id>/attributions?indices=<string:indices>&imageMode=<string:image_mode>`` -- Retrieves the attributions with the specified indices from the specified project. The indices are a comma-separated list of integers. The image mode can either be ``input``, ``overlay`` or ``attribution``, and defaults to ``input``. Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the attributions, including their index, width, height, heatmap URLs, list of labels, and prediction result of the classifier. If the specified project, or one or more of the attributions do not exist, an HTTP 404 Not Found response is returned.
* ``GET /api/projects/<int:project_id>/attributions/<int:attribution_index>?imageMode=<string:image_mode>`` -- Retrieves the attribution with the specified index from the specified project. The image mode can either be ``input``, ``overlay`` or ``attribution``, and defaults to ``input``. Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the attribution, including its index, width, height, heatmap URLs, list of labels, and prediction result of the classifier. If the specified project or attribution does not exist, an HTTP 404 Not Found response is returned.
* ``GET /api/projects/<int:project_id>/attributions/<int:attribution_index>/heatmap?colorMap=<string:color_map>&superimpose=<bool:superimpose>`` -- Renders a heatmap from the attribution with the specified index from the specified project. The color map can be one of: ``gray-red``, ``black-green``, ``black-fire-red``, ``black-yellow``, ``blue-white-red``, ``afm-hot``, ``jet``, or ``seismic``, defaults to ``black-fire-red``. The ``superimpose`` parameter can be either ``true`` or ``false``, and defaults to ``false``. Returns an HTTP 200 OK response with the rendered heatmap image. If the specified project or attribution does not exist, an HTTP 404 Not Found response is returned.
* ``GET /api/projects/<int:project_id>/analyses/<string:analysis_method_name>?category=<string:category>&clustering=<string:clustering>&embedding=<string:embedding>`` -- Retrieves the analysis from the specified project with the specified analysis method. Besides the project ID and the analysis method name, the name of the category, clustering, and embedding have to be specified in the URL parameters ``category``, ``clustering``, and ``embedding``. Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the analysis. If the specified project, analysis method, or analysis does not exist, an HTTP 404 Not Found response is returned. If no category name, clustering name, or embedding name were specified in the URL parameters, an HTTP 400 Bad Request response is returned.
* ``GET /api/color-maps`` -- Retrieves the names of all the color maps that are supported. Returns an HTTP 200 OK response with a JSON list of all the supported color maps as content.
* ``GET /api/color-maps/<string:color_map>?width=<int:width>&height=<int:height>`` -- Renders a preview of a color map with a value gradient. Using the URL parameters ``width`` and ``height``, the size of the preview can be specified. The size defaults to 200x20. Returns an HTTP 200 OK response with the rendered heatmap preview. If the specified color map is unknown, an HTTP 400 Bad Request response is returned.

When the backend REST API server is not operated in debug mode, the frontend application is automatically served via this same server, eliminating the need for an external HTTP server. Consequently, ViRelAy can be run with minimal infrastructure requirements. The frontend is accessible through the following endpoints:

* ``GET /`` or ``GET /index.html`` -- Serves the index page of the frontend.
* ``GET /<string:file_name>.css`` -- Serves the specified CSS style sheet. If the style sheet file could not be found, an HTTP 404 Not Found response is returned.
* ``GET /<string:file_name>.js`` -- Serves the specified JavaScript file. If the JavaScript file could not be found, an HTTP 404 Not Found response is returned.
* ``GET /assets/images/<string:file_name>.png`` -- Serves the specified image file. If the image file could not be found, an HTTP 404 Not Found response is returned.
* ``GET /assets/favicon/<string:file_name>`` -- Serves the specified favicon file. If the specified favicon image or manifest file could not be found, an HTTP 404 Not Found response is returned.
* ``GET /<path:file_name>`` -- A catch-all route for all other paths, which returns an HTTP 404 Not Found response.

Unit Testing
============

The backend REST API incorporates an extensive unit test suite, striving for comprehensive code coverage at all times. This test framework is housed in a dedicated directory, :repo:`tests/unit_tests`, and leverages a shared fixture module, ``conftest``, to streamline testing efforts across the ViRelAy unit test modules. Each ViRelAy module is accompanied by a corresponding test module, where tests are structured according to their respective subjects (e.g., the module ``image_processing`` has a ``test_image_processing`` test module). The `PyTest framework <https://docs.pytest.org/en/stable/>`_ framework serves as the foundation for these tests, which utilize classes and functions to validate both class-based and function-based functionality, e.g., the ``Project`` class in the ``model`` module has a matching ``TestProject`` test class, and the ``render_heatmap`` function in the ``image_processing`` module is accompanied by a ``test_render_heatmap`` function.

To ensure the highest quality of contributions, it is essential that all modifications or additions are thoroughly tested through successful execution of the test suite. The easiest way to run the unit tests is through tox. It enables you to run unit test in multiple Python environments, including Python versions 3.10 through 3.13, represented by the ``py310``, ``py311``, ``py312``, and  ``py313`` tox environments. Additionally, tox can be used to measure code coverage through the ``coverage`` environment, execute linters via the ``pylint``, ``pycodestyle`` and ``pydoclint`` environments, run the static type checker using the ``mypy`` environment, and build the documentation by running the ``docs`` environment. By invoking ``uv --directory source/backend run tox --conf ../../tests/config/tox.ini run`` in your terminal, you can execute all tox environments. To target a specific environment, leverage the ``-e`` parameter. For instance, to run unit tests for Python 3.10 and the PyLint linter, use the following command:

.. code-block:: console

    $ uv --directory source/backend run tox \
        --conf ../../tests/config/tox.ini \
        run -e py310,pylint

.. warning::

    If the ``TestServer::test_angular_frontend_is_served_when_server_is_not_in_debug_mode`` test fails due to a ``FileNotFoundError`` exception, ensure that you have built the frontend beforehand. While running the unit tests, the frontend files are served from the ``source/frontend/distribution/browser`` directory. If the frontend files are not present in this directory, then the test will fail. To build the frontend, you can use the following command:

    .. code-block:: console

        $ npm --prefix source/frontend run build

To manually execute the tests, utilize the ``pytest`` command line interface to run the unit tests located in the ``tests/unit_tests`` directory:

.. code-block:: console

    $ uv --directory source/backend run pytest ../../tests/unit_tests

This will run all tests and report how many tests where successful and how many tests failed. To ensure comprehensive code coverage, it is essential to run unit tests in conjunction with code coverage analysis. Execute the following command to run all unit tests and generate a code coverage report:

.. code-block:: console

    $ uv --directory source/backend run pytest \
        --cov virelay \
        --cov-config ../../tests/config/tox.ini \
        ../../tests/unit_tests

The ``--cov`` argument specifies the module against which the code coverage is to be measured and the ``--cov-config`` argument specifies, that the tox configuration file also contains the configuration for the test coverage. This command will output detailed code coverage statistics. For a more extensive report in the form of an HTML website, append the ``--cov-report html`` argument:

.. code-block:: console

    $ uv --directory source/backend run pytest \
        --cov virelay \
        --cov-config ../../tests/config/tox.ini \
        --cov-report html \
        ../../tests/unit_tests

The unit tests are integrated into a continuous integration (CI) pipeline, which is executed upon the creation of each pull request. Pull requests with failing CI pipelines are not accepted.

Linting
=======

The backend REST API adheres to a rigorous code style, which is enforced by utilizing tools such as `PyLint <https://www.pylint.org/>`_, `PyCodeStyle <https://pycodestyle.pycqa.org/en/latest/intro.html>`_, and `PyDocLint <https://jsh9.github.io/pydoclint/>`_` for linting, in addition to `MyPy <https://mypy-lang.org/>`_ for static type checking. These checks are integral to identifying potential runtime bugs and ensuring the quality of our codebase. It is essential that contributors regularly run these tools and rectify any warnings that arise. Moreover, it is imperative to verify the absence of warnings before committing changes or creating pull requests. The linting and static type checking process is integrated into our CI pipeline, which automatically runs upon the creation of a pull request. Any pull request resulting in a failed build will not be accepted.

The configuration files for each tool are located in the tests/config directory:

* **PyLint**: :repo:`tests/config/.pylintrc`
* **PyCodeStyle**: :repo:`tests/config/.pycodestyle`
* **PyDocLint**: :repo:`tests/config/.pydoclint.toml`
* **MyPy**: :repo:`tests/config/.mypy.ini`

Again, the easiest way to run all linters and the static type checker is through tox:

.. code-block:: console

    $ uv --directory source/backend run tox \
        --conf ../../tests/config/tox.ini \
        run -e pylint,pycodestyle,pydoclint,mypy

Alternatively, these linters and the type checker can be executed individually:

.. code-block:: console

    $ uv --directory source/backend run pylint \
        --rcfile ../../tests/config/.pylintrc \
        virelay \
        ../../tests/unit_tests \
        ../../docs/source/conf.py

    $ uv --directory source/backend run pycodestyle \
        --config ../../tests/config/.pycodestyle \
        virelay \
        ../../tests/unit_tests \
        ../../docs/source/conf.py

    $ uv --directory source/backend run pydoclint \
        --config ../../tests/config/.pydoclint.toml \
        virelay \
        ../../tests/unit_tests \
        ../../docs/source/conf.py

    $ uv --directory source/backend run mypy \
        --config-file ../../tests/config/.mypy.ini \
        virelay \
        ../../tests/unit_tests \
        ../../docs/source/conf.py

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

.. warning::

    When using ZSH instead of Bash, it is necessary to modify the globbing pattern in the script. Specifically, the wildcard notation ``docs/examples/**/*.py`` will not only match files in the sub-directories of ``docs/examples``, but also in the directory itself, which includes the files that were already matched by the ``docs/examples/*.py`` pattern. This leads to inconsistencies with MyPy, which interprets multiple instances of the same file name as distinct modules and subsequently triggers errors.
