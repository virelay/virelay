# Changelog

## v0.5.0

*Release date to be determined.*

- Updated the Python dependencies in the `setup.py` file to the their respective latest versions
  - The versions of all other packages were set to be greater than or equal to the currently latest version and are restricted to be below the next major version, so that versions with breaking changes will be installed in the future
  - Python 3.7 has already reached its end-of-life and the end-of-life of Python 3.8 is imminent. Although Python 3.9 will only reach its end of life in October 2025, it is missing the union operator "|" for type hints. Although this operator is not strictly necessary, it makes the type hinting for MyPy much easier to read. Also, the latest NumPy version does not support Python 3.9 anymore. Since ViRelAy is not a library used by other projects and since most operating systems already support Python 3.10, the minimum Python version was updated to 3.10 to make the development process easier. Python 3.11 and 3.12 were also added to the list of supported Python versions. This means that now Python 3.10, 3.11, and 3.12 are the supported Python versions for the project.
  - The following changes had to be made to because of the updated Python versions and dependencies:
    - The configuration Python file for building the documentation `docs/source/conf.py` was using the `pkg_resources` module, which has been deprecated and was removed in Python 3.12. It was replaced by the much simpler `Module.__file__` property.
    - In previous versions, Flask was using `application/javascript` as the MIME type for JavaScript files. This has now been changed to `text/javascript`. Also, in Python 3.12, Flask now uses `image/x-icon` instead of `image/vnd.microsoft.icon`. For this reason, the unit tests were updated.
    - The server previously also used the `pkg_resources` module to serve the static frontend files from the package directory. Since the module is now deprecated and was removed in Python 3.12, it was replaced with the `importlib.resources` module.
- The Sphinx build configuration and the configuration for "Read the Docs" were updated:
  - The year in the copyright notice of the documentation is now always set to the current year.
  - The way the GitHub URLs for the source code links are generated has been updated and now also supports type hints, which have to be handled differently from modules, classes, methods, and functions, because they are variables.
  - The Ubuntu and Python versions used by "Read the Docs" to build the documentation were also updated to the latest versions, i.e., Ubuntu 24.04 and Python 3.12.
- The versions of Python and the versions of the dependencies were also updated in the `tox.ini` configuration file.
- Improved the Python Linting
  - The Flake8 linter was replaced by [PyCodeStyle](https://pycodestyle.pycqa.org/en/latest/intro.html) and [PyDocLint](https://jsh9.github.io/pydoclint/), and [MyPy](https://mypy-lang.org/) was added as a static type checker. All four checkers are now included in the `setup.py` as extra dependencies under the name `linting`, so that developers can install them if they want to use them locally, e.g., as a Visual Studio Code integration.
  - New configurations for PyCodeStyle, PyDocLint, and MyPy were added and the configuration file for PyLint was updated to match the latest version of PyLint.
  - The PyLint and Flake8 test environments were removed from the `tox.ini` file and the new test environment `linting` was added, which runs all linters and the static type checker.
  - The maximum line length was increased from 120 to 150, which makes it now easier to break some longer lines
  - The Flake8 and PyLint jobs were removed from the GitHub Actions Workflow configuration file, and the new job `lint-and-type-check` was added, which runs the tox test environment "linting" to run the linters and the static type checker.
  - The documentation was updated to reflect the changes in the linting process and to explain how to run the linters and the static type checker locally.
  - In order to improve MyPy's ability to reason about the types and therefore find bugs, many type hints were added throughout the code. Also, types were introduced to make the dictionaries that are loaded from or written to YAML/JSON files strongly typed.
  - The entire code base was linted and type-checked, and all issues found by the linters and the type checker were fixed. Thanks to the new linters and the new type checker, several obscure bugs were found that would have gone unnoticed otherwise:
    1. The automatic reload of the Flask server was not working correctly, because instead of using the property "debug", the incorrect property "auto_reload" was used.
    2. The ViRelAy modules were imported using the relative import syntax instead of the absolute import syntax, which may cause problems because sometimes it is not clear if an import is relative or not, relative imports can be ambiguous, they are brittle and may break when a module is moved, and since Python 3, implicit relative imports are not allowed anymore.
    3. The `get_label...` methods of the LabelMap class returned the human-readable names of the labels instead of the labels themselves, which was not obvious from the method names. In some parts of the code, the list of human-readable names was used instead of a list of labels, which was incorrect. Now, the LabelMap has a new set of methods for retrieving the labels, and the old methods were renamed to make their purpose clearer. All instances where the methods are used were checked and corrected if necessary.
    4. In multiple instances, variables were reused, for example, variables that were used to store a NumPy array of an image were reused when creating a Pillow Image from them. This lead to some errors, where a NumPy array was expected, but a Pillow Image was passed instead, and vice versa.
    5. In many cases, the documentation for methods was either missing, incomplete, or incorrect. The documentation was updated to reflect the actual behavior of the methods.
    6. In the tests, the names of the fixtures were reused and may therefore have accidentally overwritten each other. The names of the variables and parameters were changed to be unique.
    7. The unit tests were missing a `__init__.py` file and were thus not a proper Python package. This was fixed by adding the missing file.
    8. The `__init__.py` file of the ViRelAy package did not contain a docstring, which was added.
    9. The fixtures for the unit tests are nested, which means they reference each other. Since the parameter names must match the names of the fixtures and since the fixtures were all in the same file, the parameters were shadowing the fixtures. This was fixed by renaming the fixture functions to `get_..._fixture` and adding a name to the fixture attribute.
    10. Some unit tests were incorrectly comparing `Label` objects with strings, which is now fixed.
- Added a Dockerfile for a Docker image that contains tox and all supported Python versions. This makes it easy to run the unit tests with all supported Python versions, without having to install multiple Python versions on your system. A container can be run using a convenience script that will automatically build the Docker image, if it is not already locally available, an run tox inside of it. The convenience script can be used as a drop-in replacement for tox.
- The files for the dockerized tox version are now located in sub-directory of the `tests` directory, called `docker_tox`. For this reason, the unit tests for the backend REST API, and the configuration files for the linter and the static type checker were moved into separate sub-directories of the `tests` directory, called `unit_tests` and `config`, respectively.
- Added a CSpell configuration for spell-checking the contents of the repository, checked all files, and corrected any spelling mistakes.
  - The spell-checking was also added to the GitHub Actions tests workflow. This will run the spell-checking on all files in the repository and report any misspelled words during the CI/CD process.
  - Removed LaTeX commands for accented characters from the bibliography file, as they we are using Pybtex to handle the bibliography and it has full Unicode support.
- Added a `CITATION.cff` file, which contains the necessary information to cite this repository. This file is based on the [Citation File Format (CFF)](https://citation-file-format.github.io) standard.
- The GitHub Actions Workflow configuration file was updated
  - The Workflow configuration file was cleaned up and documented.
  - The version of the `checkout` action was updated to the latest version v4.
  - The version of the `setup-python` action was updated to the latest version v5.
  - The `jobs.docs.strategy.fail-fast` option was previously used to prevent the workflow from stopping if the documentation build failed. However, this option is only supported for matrix strategies. Since the `docs` job does not use a matrix strategy, the `jobs.docs.strategy.fail-fast` option was replaced with the `jobs.docs.continue-on-error` option.
- Moved the ViRelAy logo from the `docs/images` directory a new top-level directory called `design`, in order to clean up the repository.
- Removed the `LICENSE` file. Previously, there were two license files: `COPYING`, which contained the AGPL 3.0 license text, and `LICENSE`, which contained a note about where to find the license of the project and any third-party licenses. This was done, because GPL prefers the file name `COPYING`, but back then GitHub did not support that file name. Now, GitHub also supports `COPYING`. As the information about where to find the project license and the third-party licenses is also contained in the read me, the `LICENSE` file was removed.

## v0.4.0

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
