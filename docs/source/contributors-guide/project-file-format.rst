===================
Project File Format
===================

Project files are described in `YAML <https://yaml.org/>`_. Multiple project files may be supplied on the command line. A project file may look like :repo:`docs/example/ilsvrc2012/project-sg.yaml`:

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

Paths are relative to the project file. HDF5 files are structured as described in :repo:`docs/database_specifications.md`. An example how to structure HDF5 file for use with virelay is shown in :repo:`docs/example/hdf5_structure.py`. An example for a label map is given in :repo:`docs/example/ilsvrc2012/label-map.json`.
