# Specifications for storing data
## Legend
- `keys` or `files`
- *shape*
- **data type**
- `<variable>`

- HDF5 structure
  - `key`: **group**, or **dtype** if members have same shape and no identifiers
    - if **group**, `<subkey-variable>`: **dype** variable subkey without type
      - attributes:
        - `attribute`: attribute valid for all subkeys of `key`
    - if **dtype**: *shape* same shape for all members
  - `other-key`: **group** `<clustering>` **dtype** *shape* definition for all group members
    - attributes: (attributes are used to define parameters of the used algorithm)
      - `other-attr`: **dype** *shape* all members have this attribute
    - `specific-member`: properties for some specific member of group
      - attributes
        - `some-attr`: **dtype** *shape* only `specific-member` has this attribute

## General Data Specification
- all data is stored on `vca-gpu-211-01` at `<data-root>` = `/data/shared/sprincl/`
- file names with underscores for spaces and dashes as key-seperators
- everything is HDF5
- all keys are in singular
- each data instance is one large file
  - input data is only one per dataset and model
  - attribution is one per dataset, model and attribution method
  - analysis is one per dataset, model, attribution method and analysis topic

## Model Input Data
- stored at `<data-root>/<dataset>/<model>.input.h5`
- shape for image data is *samples x channel x heigth x width*
- since preprocessing depends on the model, we supply a file `<model>.input.h5` with all preprocessing steps applied
- HDF5 structure
  - `data`: **group**, or **float32** if every sample has same dimensions
    - if **group**: `<data-id>` **float32** *channel x height x width* if group, `<data-id>` can be a filename or an identifier
    - if **float32**: **float32** *samples x channel x height x width*
  - `label`: **group**, or **uint** if data is **group**
    - if **group**: `<data-id>` **uint** *1* for single label, or **bool** *classes* for multi label
    - if **uint**: *samples* for single label, **bool** *samples x classes* for multi label if `data` is **float32**
  - `index`: **group** `<data-id>` **uint** *1*, optional
    - if `data` is **group**, assign indices to keys
    - otherwise natural sort order of keys is assumed

## Attribution of Input Data
- stored at `<data-root>/attributions/<dataset>/<model>-<attribution-method>-<attribution-strategy>.attribution.h5`
- `<attribution-strategy>` can be:
  - `true`: for true label
  - `model`: for model prediction
  - `<integer>` for choosing a fixed label
  - `<else>` for something I did not think of
- HDF5 structure
  - `index`: **uint** *samples* indices of attributed input samples in the input file
  - `attribution`: **group** or **float32** attributions with full channel information
    - if **group**: `<data-id>` **float32** *channel x height x width*
    - if **float32**: *samples x channel x height x width*
  - `label` **group** or **float32**, attribution assigned for the model output, goverened by `<attribution-strategy>`
    - if **group**: `<data-id>` *samples x {1, <classes>}*
    - if **uint**: *samples x {1, <classes>}*
  - `prediction`: **group** or **float32**
    - if **group**: `<data-id>` **float32** *classes*
    - if **float32**: *samples x classes*

## Analysis Output Data
- stored at `<data-root>/analysis/<dataset>/<model>-<attribution-method>-<attribution-strategy>-<analysis-topic>.analysis.h5`
  - `<analysis-topic>` is an identifier for the analysis approach, e.g. different distance metrics, graph methods etc.
- HDF5 structure
  - `<analysis-identifier>` **group** with name of the analysis as subkeys (not necessarily classes!, wordnet-id for classwise ImageNet Analysis)
    - `index`: **uint32** *samples* sample indices in the input attribution file, shared among embeddings
    - `embedding`: **group** `<embedding-id>`
      - `spectral`: **float32** *samples x eigenvalues* Eigenvectors of EigenDecomposition
        - attributes:
          - `eigenvalue` **float32** *eigenvalues* Eigenvalues for the spectral embedding
      - `tsne`: **float32** *samples x 2* t-SNE Embedding
        - attributes:
          - `embedding`: **string** 1 the embedding used for tsne, non-existent if T-SNE on data
          - `index`: **uint** the feature indices (not sample dimension) of the used embedding, non-existent if T-SNE on data
    - `cluster`: **group** `<clustering>` **uint32** *samples* labels for clustering on embedding
      - attributes: (attributes are used to define parameters of the used algorithm)
        - `embedding`: **string** 1 the embedding used for clustering
        - `index`: **uint** the feature (not sample dimension) indices of the used embedding
      - `kmeans-<k>`: label for clusters on the spectral embedding using k-means with k=`<k>`
        - attributes
          - `k`: **uint8** *1* k (number of clusters) for k-means
