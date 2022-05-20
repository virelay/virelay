===================
Project File Format
===================

Project files bind all the other files, belonging to a project (label map, dataset, attributions, analyses), together and contain meta information about the project. Project files are created in `YAML <https://yaml.org/>`_ format. An example of a project file for a VGG16 classifier trained on the CIFAR-10 dataset can be seen in the listing below.

.. code-block:: yaml

    project:
        name: VGG16 CIFAR-10
        model: VGG16
        label_map: label-map.json
        dataset:
            name: CIFAR-10
            type: hdf5
            path: cifar-10.h5
            input_width: 32
            input_height: 32
            up_sampling_method: none
            down_sampling_method: none
        attributions:
            attribution_method: LRP Epsilon Gamma Box
            attribution_strategy: true_label
            sources:
            - attributions.h5
        analyses:
        - analysis_method: Spectral
          sources:
          - analysis.h5

The paths of the files referenced in the project are all relative to the project file. HDF5 files are structured as described in :doc:`database-specification`. An example how to structure HDF5 files for use with ViRelAy is shown in :repo:`docs/examples/hdf5_structure.py`.

The project YAML file consists of a project name, a model name, a reference to the dataset file, a reference to the label map file, a reference to the attribution files, and a reference to the analysis files. The definition for each property is as follows:

- ``project`` → ``name``: The name of the project. Can be chosen arbitrarily and is only used for informational purposes.
- ``project`` → ``model``: The name of the classifier model. Can be chosen arbitrarily and is only used for informational purposes.
- ``project`` → ``label_map``: The path to the label map file.

- ``project`` → ``dataset``: The dataset that the classifier was trained on.
- ``project`` → ``dataset`` → ``name``: The name of the dataset. Can be chosen arbitrarily and is only used for informational purposes.
- ``project`` → ``dataset`` → ``type``: The type of the dataset, which is used to distinguish between image directory datasets and datasets that are stored in HDF5 files. Possible values are:

  - ``hdf5``: the dataset is stored in an HDF5 file, please refer to :doc:`database-specification` for more information.
  - ``image_directory``: the dataset is stored in a hierarchal directory structure, where the top-level directory contains directories for the classes and each class directory contains the samples.

- ``project`` → ``dataset`` → ``path``: The path to the HDF5 file or the directory containing the dataset.
- ``project`` → ``dataset`` → ``input_width``: The input width determines the width to which the images have to be re-sampled before feeding them into the classifier. This is needed when the dataset images have varying sizes or the classifier needs a different input size than the images of the dataset.
- ``project`` → ``dataset`` → ``input_height``: The input height determines the height to which the images have to be re-sampled before feeding them into the classifier. This is needed when the dataset images have varying sizes or the classifier needs a different input size than the images of the dataset.
- ``project`` → ``dataset`` → ``up_sampling_method``: The up-sampling methods determine how the images are scaled up when they are smaller than the specified input size. Possible values are:

  - ``none``: No up-sampling is performed.
  - ``fill_zeros``: A border of zeros will be added.
  - ``fill_ones``: A border of ones will be added.
  - ``edge_repeat``: The pixels at the edge of the image will be repeated to fill up the remaining space.
  - ``mirror_edge``: The pixels at the edge of the image will be mirrored to fill up the remaining space.
  - ``wrap_around``: The pixels from the opposite edge will be mirrored to fill up the remaining space.
  - ``resize``: The image will be scaled to the desired size.

- ``project`` → ``dataset`` → ``down_sampling_method``: The down-sampling methods determine how the images are scaled down when they are bigger than the specified input size. Possible values are:

  - ``none``: No up-sampling is performed.
  - ``center_crop``: A central part of the image with the desired size will be cut out.
  - ``resize``: The image will be scaled to the desired size.

- ``project`` → ``attributions``: The attributions that were computed for the entire dataset using the classifier model.
- ``project`` → ``attributions`` → ``attribution_method``: The name of the method that was used to compute the attributions, e.g., the name of an LRP variant.
- ``project`` → ``attributions`` → ``attribution_strategy``:

  - ``true_label``: The attribution was computed for the ground-truth label.
  - ``predicted_label``: The attribution was computed for the label predicted by the classifier.

- ``project`` → ``attributions`` → ``sources``: A list of the attribution source HDF5 files. There can be one or more attribution databases in a project, e.g., one attribution database per dataset class could be created.

- ``project`` → ``analyses``: A list of the analyses that were performed on the attributions. There can be multiple different analyses with their own analysis files in a project.
- ``project`` → ``analyses`` → ``analysis_method``: The name of the method that was used to perform the analysis, e.g., "Spectral".
- ``project`` → ``analyses`` → ``sources``: A list of the analysis source HDF5 files. Each analysis can consist of one or more analysis databases, e.g., one analysis file could be created per embedding or attribution method.

The label map is a separate file, which contains a mapping between the label index, the name of the class, and optionally the WordNet ID that corresponds to the class. The label map is used to correctly map between label indices or WordNet IDs and human-readable class names in the ViRelAy UI. The label map consists of an array of objects, where each object represents a single class with an index, a name, and an optional WordNet ID. An example for a label map for the CIFAR-10 dataset can be seen in the listing below.

.. code-block:: json

    [
        {
            "index": 0,
            "word_net_id": "n02691156",
            "name": "Airplane"
        },
        {
            "index": 1,
            "word_net_id": "n02958343",
            "name": "Automobile"
        },
        {
            "index": 2,
            "word_net_id": "n01503061",
            "name": "Bird"
        },
        {
            "index": 3,
            "word_net_id": "n02121620",
            "name": "Cat"
        },
        {
            "index": 4,
            "word_net_id": "n02430045",
            "name": "Deer"
        },
        {
            "index": 5,
            "word_net_id": "n02084071",
            "name": "Dog"
        },
        {
            "index": 6,
            "word_net_id": "n01639765",
            "name": "Frog"
        },
        {
            "index": 7,
            "word_net_id": "n02374451",
            "name": "Horse"
        },
        {
            "index": 8,
            "word_net_id": "n04194289",
            "name": "Ship"
        },
        {
            "index": 9,
            "word_net_id": "n04490091",
            "name": "Truck"
        }
    ]
