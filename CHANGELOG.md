# Changelog

## 0.4.0

Unreleased

- Added extensive documentation, which are available on [ReadTheDocs](https://virelay.readthedocs.io)
- Added a unit testing suite for the backend API, which has 100% code coverage and 100% test coverage
- Updated all external dependencies of the frontend to their latest version
- Replaced the deprecated `THREE.Geometry` with `THREE.BufferedGeometry` in the embedding renderer
- Introduced linting using PyLint and Flake8 and fixed all linting warnings
- Fixed many smaller bugs
  - The `add_border` function of the `image_processing` module added a border of ones when it was requested to add a zero border
  - Fixed a bug in the `center_ crop` function of the `image_processing` module, which in some situations cut off too much
  - Renamed blue-black-yellow color map to black-yellow for consistency
  - Fixed the return type of the `render_superimposed_heatmap` function, the return type was `PIL.Image` and is now `numpy.ndarray`
  - Renamed the `raw_heatmap` parameters to `attribution_data` in all relevant heatmap rendering functions of the `image_processing` module (raw heatmap is a term, which I used to use for attribution data, but attribution data is the common term)
  - Added validation for the `label_index_regex` and the `label_word_net_id_regex` parameters of the constructor of the `ImageDirectoryDataset` class
  - Fixed the parsing of label indices (they were not converted to integers) in the `get_sample` method of the `ImageDirectoryDataset` class
  - Fixed a NumPy warning (`bool` should be used instead `numpy.bool`)
  - Fixed the exception caught when retrieving samples from an `Hdf5Dataset` in the `get_sample` (this would cause the `get_sample` method to pass through the `IndexError` instead of raising a `LookupError` itself, when the sample was not found)
  - In the `Project` class some methods did not fail when the project was closed and others failed with wrong exceptions when the project was closed
  -  Fixed index bound checks when retrieving attributions using the `get_attribution` method of the `AttributionDatabase` (also indirectly affected the `get_attribution` method of the `Project` class)
  - When retrieving analyses using the `get_analysis` method of the `AnalysisDatabase` class, NumPy Arrays are now returned, where previously HDF5 datasets were returned
  - In the `Project` class, the check whether a project contains a dataset, attributions, or analyses was incorrect and is now fixed
  - If a project has no dataset, then retrieving samples now fails with an informative exception
  - Removed the `base_embedding` and `base_embedding_axes_indices` from embeddings, because these were not specification compliant, and the feature was never used (this was feature was also removed from the Angular Frontend)
  - Renamed instances of `eigen_value` variable names in Python code and `eigenValue` variable names in TypeScript to `eigenvalue`
  - Simplified the code in the `get_attribution_heatmap` method of the `Server` class (previously it was tested twice whether the heatmap is to be superimposed onto the input image, now this check is only performed once)
  - Removed multiple instances of dead code (code that never ran, because the conditions to run the code were always false)
  - Fixed multiple docstrings in classes, methods, and functions (this fixes incorrect documentation, typos, or partially missing documentation)

## v0.3.1

Released on July 5, 2021

- PyPI release
- updated example in README
- updated paper reference in README

## v0.3.0

Released on June 24, 2021

- Added a license (AGPL)
- Added a share button, which generates a link that restores the entire current state


## v0.2.0

Released on June 24, 2021

- Initial stable public release
