import h5py
import numpy as np


def make_group_example():
    # input file with groups with different sizes
    with h5py.File('grouped.input.h5', 'w') as fd:
        # input data group
        keys = ('a', 'b', 'c', 'd', 'e')
        shapes = (4, 5, 6, 5, 4)
        channels = 3
        g_input = fd.require_group('data')
        for key, shape in zip(keys, shapes):
            # each sample is its own dataset
            g_input[key] = np.random.normal(size=(channels, shape, shape)).astype(np.float32)

        # true label group
        labels = (0, 1, 0, 0, 1)
        g_label = fd.require_group('label')
        for key, label in zip(keys, labels):
            # here each sample is just a single number
            # alternatively, we could use a 1d-array of type bool for multi-label data
            g_label[key] = np.uint8(label)

        # we supply a custom ordering of our samples
        indices = (0, 2, 1, 3, 4)
        g_index = fd.require_group('index')
        for key, index in zip(keys, indices):
            # each sample has only one index
            g_index[key] = np.uint32(index)

    # attribution file with groups with different sizes
    with h5py.File('grouped-attr_method-2.attribution.h5', 'w') as fd:
        # we use attribute only subset of our data
        a_indices = (2, 3, 4)
        fd['index'] = np.array(a_indices, dtype=np.uint32)

        # attribution keys of our used subset
        a_keys = keys[2:]
        a_shapes = shapes[2:]
        g_attribution = fd.require_group('data')
        for key, shape in zip(a_keys, a_shapes):
            g_attribution[key] = np.random.normal(size=(channels, shape, shape)).astype(np.float32)

        # attribution labels are the assigned attribution in the output layer
        g_label = fd.require_group('label')
        a_labels = np.array([[0, 1], [0, 1], [0, 1]])
        for key, label in zip(a_keys, a_labels):
            # the output attributions can be any real number, and have the same shape as the output
            g_label[key] = a_labels.astype(np.float32)

        # predictions are the model output logits
        a_predictions = np.array([[0, 1], [.5, .5], [1, 0]])
        g_prediction = fd.require_group('prediction')
        for key, pred in zip(a_keys, a_predictions):
            g_prediction[key] = a_predictions.astype(np.float32)

    with h5py.File('grouped-attr_method-ana_topic.analysis.h5') as fd:
        # one analysis group, we call this analysis 'my first analysis'
        g_analysis = fd.require_group('my_first_analysis')

        # the used indices of the analysis, here we use all 3 in the attribution file
        g_analysis['index'] = np.array(a_indices, dtype=np.uint32)

        # embedding group
        g_embedding = g_analysis.require_group('embedding')
        # spectral embedding (eigenvalue decomposition) with key 'spectral', 2 eigenvalues, here just random data
        n_eigvals = 2
        g_embedding['spectral'] = np.random.normal(size=(len(g_analysis['index']), n_eigvals)).astype(np.float32)
        g_embedding['spectral'].attrs['eigenvalue'] = np.random.normal(size=n_eigvals).astype(np.float32)

        # T-SNE embedding with
        g_embedding['tsne'] = np.random.normal(size=(len(g_analysis['index']), 2)).astype(np.float32)
        # this T-SNE embedding is based on the spectral embedding
        g_embedding['tsne'].attrs['embedding'] = 'spectral'
        # both feature dimensions of the eigenvectors are used
        g_embedding['tsne'].attrs['index'] = np.array([0, 1], dtype=np.uint32)

        # cluster group, subkeys are clusterings
        g_cluster = g_analysis.require_group('cluster')
        # we call our random clustering 'my_clustering'
        g_cluster['my_clustering'] = np.random.randint(0, 2, size=len(g_analysis['index']))
        # we specify this clustering to be based on 'spectral'
        g_cluster['my_clustering'].attrs['embedding'] = 'spectral'
        # we use both feature dimensions for the spectral clustering
        g_cluster['my_clustering'].attrs['index'] = np.arange(g_embedding['spectral'].shape[1])


def make_dataset_example():
    # input file with datasets with identical sizes
    nsamples = 5
    shape = 7
    channels = 3
    labels = (0, 1, 0)
    with h5py.File('dataset.input.h5', 'w') as fd:
        # data samples have no identifier here and have implicit indices
        fd['data'] = np.random.normal(size=(nsamples, channels, shape, shape))
        fd['label'] = np.array(labels).astype(np.uint8)

    # attribution file with datasets
    with h5py.File('dataset-attr_method-2.attribution.h5', 'w') as fd:
        # we use attribute only subset of our data
        a_indices = (2, 3, 4)
        fd['index'] = np.array(a_indices, dtype=np.uint32)

        # attribution we only use a subset of our data
        fd['attriburion'] = np.random.normal(size=(len(a_indices), channels, shape, shape)).astype(np.float32)

        # attribution labels are the assigned attribution in the output layer
        a_labels = np.array([[0, 1], [0, 1], [0, 1]])
        # the output attributions can be any real number, and have the same shape as the output
        fd['label'] = a_labels.astype(np.float32)

        # predictions are the model output logits
        a_predictions = np.array([[0, 1], [.5, .5], [1, 0]])
        fd['prediction'] = a_predictions.astype(np.float32)

    # using datasets in the input/attribution does not change the analysis file structure
    with h5py.File('dataset-attr_method-ana_topic.analysis.h5') as fd:
        # one analysis group, we call this analysis 'my first analysis'
        g_analysis = fd.require_group('my_first_analysis')

        # the used indices of the analysis, here we use all 3 in the attribution file
        g_analysis['index'] = np.array(a_indices, dtype=np.uint32)

        # embedding group
        g_embedding = g_analysis.require_group('embedding')
        # spectral embedding (eigenvalue decomposition) with key 'spectral', 2 eigenvalues, here just random data
        n_eigvals = 2
        g_embedding['spectral'] = np.random.normal(size=(len(g_analysis['index']), n_eigvals)).astype(np.float32)
        g_embedding['spectral'].attrs['eigenvalue'] = np.random.normal(size=n_eigvals).astype(np.float32)

        # T-SNE embedding with
        g_embedding['tsne'] = np.random.normal(size=(len(g_analysis['index']), 2)).astype(np.float32)
        # this T-SNE embedding is based on the spectral embedding
        g_embedding['tsne'].attrs['embedding'] = 'spectral'
        # both feature dimensions of the eigenvectors are used
        g_embedding['tsne'].attrs['index'] = np.array([0, 1], dtype=np.uint32)

        # cluster group, subkeys are clusterings
        g_cluster = g_analysis.require_group('cluster')
        # we call our random clustering 'my_clustering'
        g_cluster['my_clustering'] = np.random.randint(0, 2, size=len(g_analysis['index']))
        # we specify this clustering to be based on 'spectral'
        g_cluster['my_clustering'].attrs['embedding'] = 'spectral'
        # we use both feature dimensions for the spectral clustering
        g_cluster['my_clustering'].attrs['index'] = np.arange(g_embedding['spectral'].shape[1])


def main():
    make_group_example()
    make_dataset_example()


if __name__ == '__main__':
    main()
