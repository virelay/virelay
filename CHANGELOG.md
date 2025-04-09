# Changelog

## v0.6.0

*Release date to be determined.*

### Backend REST API Updates in v0.6.0

- The Python versions supported by the backend REST API were updated:
  - Python 3.13.0 → 3.13.2,
  - Python 3.12.7 → 3.12.9,
  - Python 3.11.10 → 3.11.11, and
  - Python 3.10.15 → 3.10.16.
- The dependencies of the backend REST API were updated to their respective latest version.
- All linter errors that arose due to the updates were fixed.
- Previously, before running the unit tests of the backend, the frontend needed to be built manually. This was required, because the unit tests test if the frontend could be served through the backend, for which the frontend build artifacts are required. This was a cumbersome process and it required a warning in the documentation, which was not ideal, especially for new contributors. This process was automated by adding the building of the frontend to the tox configuration.

### Frontend Updates in v0.6.0

- Previously, the previews of the sample images and heatmaps were smoothed. Now, the UI offers a new feature, which allows users to select the sampling method for the images:
  - By default, the option is set to auto, which will select a method based on sizes of the sample image and the HTML element.
  - The user can, however, override this option and select either smooth or pixelated image sampling.
  - This will make it easier to inspect the sample images and the heatmaps: when the sample images and heatmaps are small, smoothing the image could potentially smear out important details, while pixelating large images could potentially hide small details.
  - The documentation was updated to include this new feature. As the feature caused some changes in the UI, the screenshots in the documentation were updated as well.
- Fixed the alternative text of the sample and heatmap images in the sample viewer. Previously, the text was `[Object object]`, which is the default string that is returned when the `toString` method of an object is called. The alternative text of the sample images and heatmaps is generated from their sample labels. The problem was, that the labels were not strings, but objects containing the label index, the WordNetId, and the human-readable name of the label.
- The frontend project was updated to Angular 19.2, Clarity Design System 6.15, and Clarity 17.9.
- The dependencies and the development dependencies of the frontend project were updated to their respective latest versions.
- The dependencies of the Node.js-based linters were updated to their respective latest versions.
- All configuration issues and linter errors that arose due to the updates were fixed.

### CI/CD Updates in v0.6.0

- The actions used in the GitHub Actions workflow configuration file were updated to their latest versions.
- Since the frontend is now built automatically using tox, the steps required to build the frontend before running the unit tests of the backend REST API were removed from the GitHub Actions workflow configuration file.

### Documentation Updates in v0.6.0

- Some minor spelling mistakes were corrected in the documentation.
- Also, the warning about having to build the frontend project before running the unit tests of the backend REST API was removed, because the frontend project is now built automatically in tox and no longer needs to be built manually.

## v0.5.0

*Released on April 10, 2025.*

### General Updates in v0.5.0

- Added a CSpell configuration for spell-checking the contents of the repository, checked all files, and corrected all spelling mistakes.
- Removed the `LICENSE` file. Previously, there were two license files: `COPYING`, which contained the AGPL 3.0 license text, and `LICENSE`, which contained a note about where to find the license of the project and any third-party licenses. This was done, because GPL prefers the file name `COPYING`, but back then GitHub did not support that file name. Now, GitHub also supports `COPYING`. As the information about where to find the project license and the third-party licenses is also contained in the read me, the `LICENSE` file was removed.
- Added a `CITATION.cff` file, which contains the necessary information to cite this repository. This file is based on the [Citation File Format (CFF)](https://citation-file-format.github.io) standard.
- Moved the ViRelAy logo from the `docs/images` directory a new top-level directory called `design`, in order to clean up the repository.

### Backend REST API Updates in v0.5.0

- Converted the project from `setuptools` and `setup.py` to the Python package and project manager [uv](https://github.com/astral-sh/uv) and `pyproject.toml`.
  - This was made necessary, because the `virelay` package was moved into a `source/backend` directory and the `frontend` project was also moved from the `virelay` package into the `source/frontend` directory, and setuptools does not allow us to include data files that are not contained in the package directory.
  - However, this also brings many advantages, since the new build system "hatchling" provides many more features and uv is not only blazing fast, it also makes the project management easier.
  - Also, the old packaging system with setuptools and `setup.py` have become dated and have to be replaced by a `pyproject.toml` anyway.
- Updated the Python dependencies of the backend REST API project to their respective latest versions.
  - The versions of all other packages were set to be greater than or equal to the currently latest version and are restricted to be below the next major version, so that versions with breaking changes will not be installed in the future (although, this is prevented by the `uv.lock` file, which locks the currently installed versions of the packages to specific versions).
- Performed some minor updates on the backend REST API project:
  - Instead of having an application class in the backend REST API, which basically only had a running method, the application now has a run function for the CLI and a run function for the UWSGI server. Starting the UWSGI server already was a function, because GUnicorn does not support the use of methods when starting the server. This makes the code more consistent.
  - To facilitate the loading of multiple dataset samples simultaneously, a new endpoint was added, which allows users to provide a list of sample IDs.
  - Instead of having an `Application` class in the backend REST API, which basically only had a `run` method, the application now has a `run_cli_app` function for the CLI and a `run_wsgi_app` function for the UWSGI server. Starting the UWSGI server already was a function, because GUnicorn does not support the use of methods when starting the server. This makes the code more consistent.
  - The endpoints of the REST API were available using any HTTP verb. Now, only the GET method is allowed.
  - The default port of the backed REST API was changed to 8000, because 8080 is more commonly used and might conflict with other services. The documentation was updated accordingly.
  - Version, author, license, and copyright information of the backend REST API was added to the `__init__.py` file. The version is automatically updated from the current Git tag during build.
  - When serving the frontend files, the backend now checks if the file exists and returns HTTP 404 Not Found, if the file could not be found, instead of raising an exception, which results in an HTTP 500 Internal Server Error.
- The list of supported Python versions was updated
  - Python 3.7 has already reached its end-of-life and the end-of-life of Python 3.8 is imminent. Although Python 3.9 will only reach its end of life in October 2025, it is missing the union operator `|` for type hints. Although this operator is not strictly necessary, it makes the type hinting for MyPy much easier to read. Also, the latest NumPy version does not support Python 3.9 anymore. Since ViRelAy is not a library that is used by other projects and most operating systems already support Python 3.10, the minimum Python version was updated to 3.10 to make the development process easier. Python 3.11, 3.12, and 3.13 were also added to the list of supported Python versions. This means that now Python 3.10, 3.11, 3.12, 3.13 are the supported Python versions for the project.
  - The following changes had to be made to because of the updated Python versions and dependencies:
    - In previous versions, Flask was using `application/javascript` as the MIME type for JavaScript files. This has now been changed to `text/javascript`. Also, in Python 3.12, Flask now uses `image/x-icon` instead of `image/vnd.microsoft.icon`. For this reason, the unit tests were updated.
    - The server previously used the `pkg_resources` module to serve the static frontend files from the package directory. The module has been deprecated and was removed in Python 3.12, it was replaced with the `importlib.resources` module.
- Improved the Python Linting
  - The Flake8 linter was replaced by [PyCodeStyle](https://pycodestyle.pycqa.org/en/latest/intro.html) and [PyDocLint](https://jsh9.github.io/pydoclint/), and [MyPy](https://mypy-lang.org/) was added as a static type checker. All four checkers are included as development dependencies in the `pyproject.toml` project file.
  - New configurations for PyCodeStyle, PyDocLint, and MyPy were added and the configuration file for PyLint was updated to match the latest version of PyLint.
  - The `flake8` test environment was removed from the `tox.ini` file and the new test environments `pycodestyle`, `pydoclint` and `mypy` were added, which run the linters and the static type checker.
  - The maximum line length was increased from 120 to 150, which makes it now easier to break some longer lines
  - The Flake8 job was removed from the GitHub Actions Workflow configuration file, and the new jobs `pycodestyle`, `pydoclint` and `mypy` were added, which run the tox environments for the respective linter and the static type checker.
  - The documentation was updated to reflect the changes in the linting process and to explain how to run the linters and the static type checker locally.
  - In order to improve MyPy's ability to reason about the types and therefore find bugs, many type hints were added throughout the code. Also, types were introduced to make the dictionaries that are loaded from or written to YAML/JSON files strongly typed.
  - The configuration files for the linters and the static type checker are located in a `config` directory that is a sub-directory of the `tests` directory. For this reason, the unit tests were also moved to a sub-directory called `unit_tests`.
  - The entire code base was linted and type-checked, and all issues found by the linters and the type checker were fixed. Thanks to the new linters and the new type checker, several obscure bugs were found that would have gone unnoticed otherwise:
    1. The automatic reload of the Flask server was not working correctly, because instead of using the property `debug`, the incorrect property `auto_reload` was used.
    2. The ViRelAy modules were imported using the relative import syntax instead of the absolute import syntax, which may cause problems because sometimes it is not clear if an import is relative or not, relative imports can be ambiguous, they are brittle and may break when a module is moved, and since Python 3, implicit relative imports are not allowed anymore.
    3. The `get_label...` methods of the LabelMap class returned the human-readable names of the labels instead of the labels themselves, which was not obvious from the method names. In some parts of the code, the list of human-readable names was used instead of a list of labels, which was incorrect. Now, the LabelMap has a new set of methods for retrieving the labels, and the old methods were renamed to make their purpose clearer. All instances where the methods are used were checked and corrected if necessary.
    4. In multiple instances, variables were reused, for example, variables that were used to store a NumPy array of an image were reused when creating a Pillow Image from them. This lead to some errors, where a NumPy array was expected, but a Pillow Image was passed instead, and vice versa.
    5. In many cases, the documentation for methods was either missing, incomplete, or incorrect. The documentation was updated to reflect the actual behavior of the methods.
    6. In the tests, the names of the fixtures were reused and may therefore have accidentally overwritten each other. The names of the variables and parameters were changed to be unique.
    7. The unit tests were missing a `__init__.py` file and were thus not a proper Python package. This was fixed by adding the missing file.
    8. The `__init__.py` file of the ViRelAy package did not contain a docstring, which was added.
    9. The fixtures for the unit tests are nested, which means they reference each other. Since the parameter names must match the names of the fixtures and since the fixtures were all in the same file, the parameters were shadowing the fixtures. This was fixed by renaming the fixture functions to `get_..._fixture` and adding a name to the fixture attribute.
    10. Some unit tests were incorrectly comparing `Label` objects with strings, which is now fixed.
- The tox configuration file was updated
  - The configuration file was generally cleaned up and is now completely documented.
  - `tox-uv` is used so that tox uses uv as package manager.
  - The new linters and the type checker are now included, and the they also lint and type-check the unit tests, the Sphinx configuration script and the example scripts in the documentation.
- Updated the unit tests to reflect the changes in the backend API and to reach 100% test coverage again.

### Frontend Updates in v0.5.0

- Migrated the frontend project from Angular 13 and Clarity 13 to Angular 18 and Clarity 17.
- Updated the dependencies and the development dependencies of the frontend project to their respective latest versions.
- Cleaned up the frontend project:
  - The directory hierarchy of the project was overhauled:
    - The project was previously nested in another `src` directory, which is weird, because the project is not at the top-level of the repository, but in a source directory itself. For this reason, the files were moved out of the `src` directory, one level up, and are now in the same directory as the `angular.json`, `package.json`, and `tsconfig.json` files.
    - The `main.ts` and `index.html` files were moved into the `app` directory.
    - The `components` and `modules` directories were moved out of the `app` directory into the top-level directory of the project and `modules` was renamed to `pages`, because it only contains components that are pages. The new structure dictates that components that represent pages are in the `pages` directory and components that represent user controls and are used in other components are in the `components` directory.
    - The Sass stylesheets were moved into a top-level `styles` directory.
    - The favicon was moved into the `assets` directory.
  - The Angular and TypeScript configurations were completely overhauled and commented.
  - A favicon with support for all browsers, iOS, and Android with support for light and dark themes was created.
  - The module paths are now remapped to `@app`, `@components`, `@pages`, and `@services`, which makes it nicer to import them, because no relative paths are needed anymore.
- Performed some minor updates on the frontend:
  - The components are now standalone, which means that they are no longer included in any modules and can be loaded individually.
  - Proper error handling for the bootstrap process was integrated.
  - Also, the error handling on the project page was improved. To make it easier to display error messages, a new error message component was created.
  - In addition to the light theme, a dark theme was added. The theme is automatically selected based on the user's system preferences. The screenshots in the documentation were updated accordingly.
  - The toolbox and the sample viewer can now be scrolled horizontally using the mouse wheel, which makes them easier to navigate.
  - When hovering over an embedding vector, the corresponding sample is now loaded after a short delay, which prevents the constant loading of samples when the user only moves the mouse over the samples.
  - The samples and attributions in the selected samples viewer are now loaded all at once instead of loading the one by one.
  - The selected samples viewer is now responsive and decreases its height when the browser window gets smaller
  - Many data structures that were previously inline types or a mixture of built-in types now have proper types. This includes:
    - A type for embedding vectors,
    - a type for the hover event in the embedding visualizer,
    - a type for the coordinates of the selection box in the embedding visualizer,
    - an interface for the configuration of the application,
    - a type for clusters of embedding vectors,
    - a type for the attributions of embedding vectors,
    - an interface for HTML input events, and
    - an enumeration for the attribution image modes.
  - The state management is now done using an enumeration for the different states that a resource can be in, instead of using booleans.
  - A custom exception type for errors that occur in a service was added.
  - A URL builder was created, which makes it easier to build URLs for the backend REST API in the services.
- The build output of the frontend was removed from the repository, as it will now be build as needed. The CI/CD pipeline, as well as the documentation were adapted accordingly.
- Added multiple linters for the frontend:
  - ESLint, a JavaScript and TypeScript linter.
  - Stylelint, a CSS and Sass linter.
  - HTML-Validate, an HTML linter.
  - All issues that were detected by the linters was fixed.
  - The documentation was updated to include instructions on how to run the linters.
  - The GitHub Actions workflow configuration was adapted to run the linters.

### CI/CD Updates in v0.5.0

- The GitHub Actions Workflow configuration file was updated
  - The Workflow configuration file was cleaned up and documented.
  - The version of the `checkout` action was updated to the latest version v4.
  - Instead of using the `setup-python` action, we now use the `astral-sh/setup-uv` action to install uv, which is then used to install Python, which means that the exact same Python version that is used locally is also used in the CI/CD pipeline.
  - The `jobs.docs.strategy.fail-fast` option was previously used to prevent the workflow from stopping if the documentation build failed. However, this option is only supported for matrix strategies. Since the `docs` job does not use a matrix strategy, the `jobs.docs.strategy.fail-fast` option was replaced with the `jobs.docs.continue-on-error` option.
- The spell-checking was also added to the GitHub Actions tests workflow. This will run the spell-checking on all files in the repository and report any misspelled words during the CI/CD process.
- Set up a new GitHub Actions workflow that automatically publishes the ViRelAy package to the Python Package Index (PyPI) when a new release is created on GitHub.

### Documentation Updates in v0.5.0

- The Sphinx build configuration and the configuration for "Read the Docs" were updated:
  - The year in the copyright notice of the documentation is now always set to the current year.
  - The way the GitHub URLs for the source code links are generated has been updated and now also supports type hints, which have to be handled differently from modules, classes, methods, and functions, because they are variables.
  - The Ubuntu and Python versions used by "Read the Docs" to build the documentation were also updated to the latest versions, i.e., Ubuntu 24.04 and Python 3.12.
- The configuration Python file for building the documentation `docs/source/conf.py` was using the `pkg_resources` module, which has been deprecated and was removed in Python 3.12. It was replaced by the much simpler `Module.__file__` property.
- Removed LaTeX commands for accented characters from the bibliography file, as they we are using Pybtex to handle the bibliography and it has full Unicode support.
- All articles in the documentation were completely rewritten to sound more professional and many small mistakes were corrected.
- A bug was fixed, which caused some of the links to the repository to be broken. Links to the repository are specified as relative paths in the reStructuredText source files of the documentation articles. During the build step, they are prepended with the actual repository URL. This URL already contained the path to the `source` directory, which meant that all links to top-level files were incorrect.
- Some of the screenshots of the UI were updated to showcase the new dark-mode UI.
- A plugin was added, which causes all external links to be opened in a new tab.
- The paragraphs in the documentation are now justified.
- Updated the repository read me to reflect the changes to the project and the documentation, and added shields.io badges for the license, the build status and the latest version.

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
