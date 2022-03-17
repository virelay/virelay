================
 Getting started
================


Install
-------

ViRelAy can be installed directly from PyPI:

.. code-block:: console

   $ pip install virelay

For the current development version, or to try out examples, clone and install
with:

.. code-block:: console

   $ git clone https://github.com/virelay/virelay.git
   $ pip install ./virelay

Basic Usage
-----------

ViRelAy can be run e.g. with Gunicorn (``pip install gunicorn``) using:

.. code-block:: console

    $ gunicorn -w 4 -b 127.0.0.1:8080 \
        "virelay.application:create_app(projects=['path/to/project1.yaml', 'project2.yaml'])"


With the above, the server binds to 127.0.0.1 on port 8080 and uses 4 worker
processes.

Alternatively, the environment variable ``VIRELAY_PROJECTS`` may be used to
specify the project paths:

.. code-block:: console

    $ export VIRELAY_PROJECTS="path/to/project1.yaml:project2.yaml"
    $ gunicorn -w 4 -b 127.0.0.1:8080 "virelay.application:create_app()"

Passing the projects explicitly to ``create_app()`` takes precedence over the
environment variable, i.e. if ``create_app(projects=...)`` is used,
``VIRELAY_PROJECTS`` is ignored.


Project Files
^^^^^^^^^^^^^
Project files are described in `YAML <https://yaml.org/>`_. Multiple project
files may be supplied on the command line. A project file may look like
:repo:`docs/example/ilsvrc2012/project-sg.yaml`:

.. code-block:: yaml

    project:
      name: VGG16 ILSVRC2012-small SG
      model: VGG16
      label_map: datasets/ilsvrc2012/label-map-keras.json
      dataset:
        name: ILSVRC2012-small
        type: hdf5
        path: datasets/ilsvrc2012/ilsvrc2012-small.input.h5
        input_width: 224
        input_height: 224
        down_sampling_method: none
        up_sampling_method: none
      attributions:
        attribution_method: smoothgrad
        attribution_strategy: true_label
        sources:
          - ilsvrc2012-small-sg/attribution/ilsvrc2012-small.smoothgrad.h5
      analyses:
        - analysis_method: spectral_analysis
          sources:
            - ilsvrc2012-small-sg/analysis/ilsvrc2012-small.smoothgrad.h5

Paths are relative to the project file. HDF5 files are structured as described
in :repo:`docs/database_specifications.md`. An example how to structure hdf5
file for use with virelay is shown in :repo:`docs/example/hdf5_structure.py`. An
example for a label map is given in
:repo:`docs/example/ilsvrc2012/label-map.json`.

Example Project
^^^^^^^^^^^^^^^

An example project with random data can be created with some random data in the
following way:

Set up requirements:

.. code-block:: console

    $ mkdir virelay-example
    $ cd virelay-example
    $ # Create a virtual environment and install virelay and corelay:
    $ python -m venv .venv
    $ .venv/bin/pip install 'corelay[umap,hdbscan]' virelay
    $ # download example scripts
    $ curl -o 'make_test_data.py' \
        'https://raw.githubusercontent.com/virelay/virelay/master/docs/example/test-project/make_test_data.py'
    $ curl -o 'meta_analysis.py' \
        'https://raw.githubusercontent.com/virelay/virelay/master/docs/example/test-project/meta_analysis.py'
    $ curl -o 'make_project.py' \
        'https://raw.githubusercontent.com/virelay/virelay/master/docs/example/test-project/make_project.py'

Create the test project:

.. code-block:: console

    $ # Create some test data:
    $ mkdir -p test-project
    $ .venv/bin/python make_test_data.py \
        test-project/input.h5 \
        test-project/attribution.h5 \
        test-project/label-map.json
    $ # Execute an analysis:
    $ .venv/bin/python meta_analysis.py \
        test-project/attribution.h5 \
        test-project/analysis.h5 \
        --label-map test-project/label-map.json
    $ # Create a project file:
    $ .venv/bin/python make_project.py \
        test-project/input.h5 \
        test-project/attribution.h5 \
        test-project/analysis.h5 \
        test-project/label-map.json \
        --project-name 'Test Project' \
        --dataset-name 'Random Data' \
        --model-name 'No Model' \
        --attribution-name 'Random Attribution' \
        --analysis-name 'Spectral Analysis' \
        --output test-project/project.yaml

Now you can run virelay using the created project file:

.. code-block:: console

    $ .venv/bin/gunicorn -w 4 -b 127.0.0.1:8080 \
        "virelay.application:create_app(projects=['test-project/project.yaml'])"

Development
-----------

ViRelAy consists of 2 parts, the backend written in Python using Flask, and the
frontend implemented using Angular. A production-ready version of the frontend
is included in the repository, so it can be directly served by Flask. In case
the frontend needs to be compiled, first the dependencies need to be installed
using:

.. code-block:: console

    $ cd virelay/frontend
    $ npm install

Then the frontend may be compiled with:

.. code-block:: console

    $ node_modules/@angular/cli/bin/ng build --prod

where the ``--prod`` flag introduces optimizations for production and may be
omitted during development. The frontend's static files are produced in
``virelay/frontend/distribution`` and may then be served.

Alternatively, during development, instead

.. code-block:: console

    $ node_modules/@angular/cli/bin/ng serve

can be used for debugging purposes.

The backend server can be run using the following command (assuming you
installed a virtual environment as described above):

.. code-block:: console

    $ .venv/bin/python -m virelay --debug-mode <project-file> [<project-file>, ...]

The ``--debug-mode`` flag starts the backend server in debug mode, which prints
out detailed server logs, starts FLASK in debug mode (FLASK will print out a
debugger pin that can be used to attach a debugger), activates auto-reload when
files have changed, and will not serve the frontend via FLASK. This way, the
frontend and backend can be worked on independent from each other.

The (slow) development server provides the following interface:

.. code-block:: console

    $ virelay --help
    usage: virelay [-h] [-H HOST] [-p PORT] [-d] project [project ...]

    The visualization tool ViRelAy.

    positional arguments:
      project               The project file that is to be loaded into the
                            workspace. Multiple project files can be specified.

    optional arguments:
      -h, --help            show this help message and exit
      -H HOST, --host HOST  The name or IP address at which the server should
                            run. Defaults to "localhost".
      -p PORT, --port PORT  The port at which the server should run. Defaults to
                            8080.
      -d, --debug-mode      Determines whether the application is run in debug
                            mode. When the application is in debug mode, all
                            FLASK and Werkzeug logs are printed to stdout, FLASK
                            debugging is activated (FLASK will print out the
                            debugger PIN for attaching the debugger), and
                            automatic reloading (when files change) is
                            activated. Furthermore, the frontend of the
                            application will not be served by flask and instead
                            has to be served externally (e.g. via ng serve).
