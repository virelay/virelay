===============
Example Project
===============

An example project with random data can be created with some random data in the following way:

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
