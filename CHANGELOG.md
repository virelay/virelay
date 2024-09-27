# Changelog

## 0.5.0

*Release date to be determined.*

- Updated the dependencies in the setup.py file to the their respective latest versions
  - NumPy was pinned to the version 2.0.2, because this is the last version that seems to be compatible with Python 3.9
  - The versions of all other packages were set to be greater than or equal to the currently latest version and are restricted to be below the next major version, so that versions with breaking changes will be installed in the future
  - Python 3.7 has already reached its end-of-life and the end-of-life of Python 3.8 is imminent, therefore they were removed from the supported version of Python, and the versions 3.10, 3.11 and 3.12 were added, which means that now Python 3.9, 3.10, 3.11, and 3.12 are the supported Python versions for the project.
  - The following changes had to be made to because of the updated Python versions and dependencies:
    - The configuration Python file for building the documentation `docs/source/conf.py` was using the `pkg_resources` module, which has been deprecated and was removed in Python 3.12. The `importlib.metadata` module is now used as a replacement.
    - In a previous version, Flask used `application/javascript` as the MIME type for JavaScript files. However, the correct MIME type is `text/javascript`, which is now also used by Flask. For this reason, the unit test for it was updated.
    - The server previously also used the `pkg_resources` module to serve the static frontend files from the package directory. Since the module is now deprecated and was removed in Python 3.12, it was replaced with the `importlib.resources` module.
- In the GitHub Actions workflow configuration file, the `jobs.docs.strategy.fail-fast` option was previously used to prevent the workflow from stopping if the documentation build failed. However, this option is only supported for matrix strategies. Since the `docs` job does not use a matrix strategy, the `jobs.docs.strategy.fail-fast` option was replaced with the `jobs.docs.continue-on-error` option.

## 0.4.0

*Released on May 31, 2022.*

- Added extensive documentation, which is available on [ReadTheDocs](https://virelay.readthedocs.io)
- Added a unit testing suite for the backend API, which has 100% code coverage
- Polished and extended the scripts for generating a random test project and a real-world project
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
  - Fixed index bound checks when retrieving attributions using the `get_attribution` method of the `AttributionDatabase` (also indirectly affected the `get_attribution` method of the `Project` class)
  - When retrieving analyses using the `get_analysis` method of the `AnalysisDatabase` class, NumPy Arrays are now returned, where previously HDF5 datasets were returned
  - In the `Project` class, the check whether a project contains a dataset, attributions, or analyses was incorrect and is now fixed
  - If a project has no dataset, then retrieving samples now fails with an informative exception
  - Removed the `base_embedding` and `base_embedding_axes_indices` from embeddings, because these were not specification compliant, and the feature was never used (this was feature was also removed from the Angular Frontend)
  - Renamed instances of `eigen_value` variable names in Python code and `eigenValue` variable names in TypeScript to `eigenvalue`
  - Simplified the code in the `get_attribution_heatmap` method of the `Server` class (previously it was tested twice whether the heatmap is to be superimposed onto the input image, now this check is only performed once)
  - Removed multiple instances of dead code (code that never ran, because the conditions to run the code were always false)
  - Fixed multiple docstrings in classes, methods, and functions (this fixes incorrect documentation, typos, or partially missing documentation)
  - Fixed a bug in the heatmap rendering, where the resulting heatmap had an extra dimension, which caused the conversion to a PNG to fail
  - Fixed a bug in the eigenvalue plot in the frontend, where, when an embedding did not use eigenvalue decomposition or there are no eigenvalues available for the embedding, then the ViRelAy frontend raised an error, now the eigenvalue plot is simply not displayed when an embedding has no eigenvalues
  - Fixed a bug in the overlay image mode of ViRelAy, when there was no negative component in an attribution, then the heatmap was displayed instead of the heatmap superimposed onto the input image
  - When superimposing a heatmap onto an input image, the negative and positive components are now weighted equally, thus making the negative and positive attribution parts comparable

## v0.3.1

*Released on July 5, 2021.*

- PyPI release
- updated example in README
- updated paper reference in README

## v0.3.0

*Released on June 24, 2021.*

- Added a license (AGPL)
- Added a share button, which generates a link that restores the entire current state

## v0.2.0

*Released on June 24, 2021.*

- Initial stable public release
