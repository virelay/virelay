# Specifications for storing data
## Legend
- `keys` or `files`
- *shape*
- **data type**
- `<variable>`

- HDF5 structure
  - `key`: **group**
    - `<subkey-variable>`: variable subkey without type
      - attributes:
        - `attribute`: attribute valid for all subkeys of `key`
    - `subkey`: **data type** *shape* fixed subkey of group `key`, effectively `key/subkey` in the hierarchy
      - attributes:
        - attributes that only apply explicitly to `key/subkey`

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
  - `data`: **group** or **float32** if every sample has same dimensions
    - `<data-id>` **float32** *channel x height x width* if group, `<data-id>` can be a filename or an identifier
  - `label`: **group**, or **uint** *samples* for single label, **bool** *samples x classes* for multi label if `data` is **float32**
    - `<data-id>` **uint** *1* for single label or **bool** *classes* for multi label, if group, `<data-id>` is the same as in `data`
  - `index`: **group**, optional, if `data` is a group, assign indices to keys, otherwise natural sort order of keys is assumed
    - `<data-id>` **int** *1* `<data-id> is the same as `data`

## Attribution of Input Data
- stored at `<data-root>/attributions/<dataset>/<model>-<attribution-method>.attribution.h5`
- HDF5 structure
  - `attribution`: **float32** *samples x channel x height x width* or **group** Attributions with full channel information
    - if group, keys are the same as in input data
  - `label` **uint16** *samples x {1, <classes>}* or **group**
    - if group, keys are the same as in input data
  - `prediction` **float32** *samples x classes* or **group**
    - if group, keys are the same as in input data

## Analysis Output Data
- stored at `<data-root>/analysis/<dataset>/<model>-<attribution-method>-<analysis-topic>.analysis.h5`
  - `<analysis-topic>` is an identifier for the analysis approach, e.g. different distance metrics, graph methods etc.
- HDF5 structure
  - `<analysis-identifier>` **group** with name of the analysis as subkeys (not necessarily classes!, wordnet-id for classwise ImageNet Analysis)
    - `index`: **uint32** *samples* Sample indices in the input attribution file
    - `eigenvalue`: **float32** *eigenvalues* Eigenvalues for the spectral embedding
    - `eigenvector`: **float32** *samples x eigenvalues* Eigenvectors for the spectral embedding
    - `cluster`: **group** of clustering methods
      - `<clustering>` **uint32** *samples* labels for clustering on spectral embedding with name `<clustering>`
        - attributes: (attributes are used to define parameters of the used algorithm)
          - `eigenvector`: **uint** the indices of the used eigenvectors
      - `kmeans-<k>`: **uint32** *samples* Label for clusters on the spectral embedding using k-means with k=`<k>`
        - attributes
          - `k`: **uint8** *1* k (number of clusters) for k-means
    - `visualization`: **group** Additional embedding used for visualization with name `<name>`
      - `<name>`: visualization method with name `<name>`
        - attributes:
          - `eigenvector`: **uint32** the indices of the used eigenvectors
      - `tsne`: **float32** *samples x 2* t-SNE Embedding
