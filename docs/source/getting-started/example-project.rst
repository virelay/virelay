===============
Example Project
===============

Creating a project from a classifier and a dataset can be very complex and involved, so if you are just getting started with ViRelAy and only want to get your feet wet, a test project can be randomly generated using a set of scripts available in the ViRelAy GitHub repository.

If you have installed ViRelAy from the project's Git repository, then you already have the scripts available under ``<project-root>/docs/examples/test-project``. If you installed ViRelAy from PyPi, then you can download the latest version of the test project scripts from the repository like so:

.. code-block:: console

    $ mkdir test-project
    $ cd test-project
    $ curl -o 'make_test_data.py' 'https://raw.githubusercontent.com/virelay/virelay/master/docs/examples/test-project/make_test_data.py'
    $ curl -o 'meta_analysis.py' 'https://raw.githubusercontent.com/virelay/virelay/master/docs/examples/test-project/meta_analysis.py'
    $ curl -o 'make_project.py' 'https://raw.githubusercontent.com/virelay/virelay/master/docs/examples/test-project/make_project.py'

The test project scripts require CoRelAy to be installed, which is also available on PyPi and can be installed using your favorite Python package manager, e.g., ``pip``. It is recommended to create a virtual environment in order to not pollute your base environment. The test project scripts support many different clustering and embedding methods. To use the UMAP embedding method and the HDBSCAN clustering method, the optional support for them has to be installed as well. This can be done like so:

.. code-block:: console

    $ python -m venv venv
    $ source venv/bin/activate
    $ pip install 'corelay[umap,hdbscan]'

A ViRelAy project consists of multiple files. In its most basic configuration a dataset, a label map, an attribution database, an analysis database, and a project file are required. The dataset is either in HDF5 format or an image directory containing the dataset samples in a directory structure, where each sub-directory represents a single class. The dataset contains all images that the classifier was trained on. The label map is a JSON file, which contains a mapping between the label index, the name of the class, and optionally the WordNet ID that corresponds to the class. The label map is used to correctly map between label indices or WordNet IDs and human-readable class names in the ViRelAy UI. The attribution database is an HDF5 file that contains the attributions for each dataset sample, that were computed using the classifier and a certain attribution method (e.g., using the Zennit framework). Each project can only contain attributions for a single attribution method, but it can contain multiple attribution databases (e.g., an attribution database could be created per class). The analysis database is an HDF5 file, which contains the results of an analysis pipeline that was created using CoRelAy. These results are a set of embeddings and clusterings thereof. Each project can contain multiple analyses (e.g., to compare different analysis methods), which each can consists of multiple analysis databases (e.g., an analysis database could be created per embedding method). The project file is a YAML file, which binds all the other files together and contains some meta information about the project. For more information about the database and project file structures, please refer to the articles :doc:`../contributors-guide/database-specification` and :doc:`../contributors-guide/project-file-format`.

To generate a random dataset, a label map, and attributions for the samples in the dataset (the attributions are generated randomly as well, and are not from a real classifier), the ``make_test_data.py`` script can be used as follows:

.. code-block:: console

    $ mkdir -p test-project
    $ .venv/bin/python make_test_data.py \
        test-project/input.h5 \
        test-project/attribution.h5 \
        test-project/label-map.json

A meta-analysis of the data can then be generated using the ``meta_analysis.py`` script, which takes the attributions as input and runs them through a CoRelAy meta-analysis pipeline. The pipeline generates spectral embeddings, t-SNE embeddings and UMAP embeddings, and clusters them using agglomerative clustering, DBSCAN clustering, HDBSCAN clustering, and k-nearest neighbor clustering with various different parameters.

.. code-block:: console

    $ .venv/bin/python meta_analysis.py \
        test-project/attribution.h5 \
        test-project/analysis.h5 \
        --label-map test-project/label-map.json

Finally, to generate a project file for the randomly generated data, the ``make_project.py`` script can be used like so:

.. code-block:: console

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

The resulting project can then be opened in ViRelAy using the following command:

.. code-block:: console

    $ python -m virelay test-project/project.yaml
