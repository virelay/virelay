=================
How to Contribute
=================

ViRelAy is an open source project that depends on its community, and we're excited you're interested in joining us! We are always eager to receive contributions and appreciate your enthusiasm. If you would like to contribute, there are many ways you can help out. You can file bugs or feature request, update the documentation, or even contribute code to the project.

To get started with contributing, we recommend reading our :doc:`../user-guide/index` to familiarize yourself with the project. It contains a compilation of helpful tips to get you started, and it will give you a solid understanding of how our system works and what aspects of it need improvement. It also contains in-depth articles on the internals of ViRelAy such as the :doc:`database-specification` and the :doc:`project-file-format`. ViRelAy consists of 2 parts: the backend REST API written in Python and `Flask <https://flask.palletsprojects.com/en/2.1.x/>`_, and the frontend, which is was created using `Angular <https://angular.io/>`_ and `Clarity <https://clarity.design/>`_. Please read the articles :doc:`backend-rest-api` and :doc:`frontend` for more information.

Filing Bugs & Feature Requests
==============================

If you've encountered a bug or have a feature request, please let us know by opening an issue on the project's `GitHub page <https://github.com/virelay/virelay/issues>`_. Before doing so, we recommend checking the existing issues to avoid duplication of work and ensure that your report adds value. If so, then please add any information to the existing issue that might help us resolve it fast. Only open a new issue if there are no other issues concerning the same problem.

When opening an issue, please provide as much information as possible. This will greatly help us identify and resolve the issue efficiently. Some examples of useful system information include:

* Your operating system and version (Windows 11, macOS 15, Ubuntu 24.04, etc.)
* The version of ViRelAy you're running
* Any relevant configuration settings or dependencies

When filing a bug report, please provide a detailed step-by-step guide on how to reproduce the issue. This will enable us to diagnose and fix the problem more quickly.

Contributing Code or Documentation
==================================

Before starting to contribute code, please check if there is already an existing issue that aligns with your ideas. This will help us avoid duplication of effort and ensure that your contributions are integrated smoothly into the project. If there is no issue concerning your contribution ideas, we would still appreciate if you would open an issue first, where you explain what you want to do. This helps to align your ideas with the rest of the team and may prevent you from doing work, that the team is already planning on doing. To get started, follow these steps:

1. Fork the Repository
----------------------

Fork the project's repository on GitHub to create a copy of it under you own account. After cloning your fork, please create a new feature branch with a descriptive name. We use kebab case for branch names, i.e., lower-case words separated by hyphens, for example, ``my-new-feature``.

2. Make your Changes
--------------------

Make the necessary changes to the codebase. Please comment and document your code extensively. We `Google-style Docstrings <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_ for the backend REST API and the `JSDoc <https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html>`_ format for the frontend. We encourage you to follow our established coding conventions and avoid making unnecessary changes to the code style. We know that it is tempting to change the code style of a project to your liking, but this will produce unnecessary effort and will only lead to constant style changes. To help you with this, we use various tools to enforce the code style, detect code smells, prevent many forms of bugs, and statically type-check the backend REST API:

* **`PyLint <https://www.pylint.org/>`_** -- Enforces the code style and detects potential issues and bugs.
* **`PyCodeStyle <https://pycodestyle.pycqa.org/en/latest/intro.html>`_** -- Checks the code style consistency.
* **`PyDocLint <https://jsh9.github.io/pydoclint/>`_** -- Ensures proper documentation and that the style of the Docstrings is correct.
* **`MyPy <https://mypy-lang.org/>`_** -- Statically type-checks the backend REST API.

Please make sure that neither of them produces warnings before committing. Never adapt the configuration of PyLint, PyCodeStyle, PyDocLint, or MyPy unless you have a really good reason to do so (please tell us about your reasoning in the accompanying issue or the pull request).

3. Build the Frontend
---------------------

If you have made changes to the frontend, then please build it using the ``production`` configuration and put the build artifacts into the :repo:`source/frontend/distribution` directory. This is necessary, because the built frontend is included in the ViRelAy Python wheel package.

4. Write Tests
--------------

Write unit tests for the features you have added. We aim to have a test coverage of 100% for the backend REST API (the frontend does not have a test suite, yet). Make sure all tests pass before committing.

5. Update the tox Configuration & GitHub Actions Workflow
---------------------------------------------------------

The unit tests, the linters, the static type checker, and the build of the documentation is run using tox. They are also run as part of our CI/CD pipeline on GitHub Actions. If you have made any changes that require changes to the tox configuration or the GitHub Actions workflow, please ensure that the relevant sections are updated. The configuration files can be found in the :repo:`tests/config/tox.ini` and :repo:`.github/workflows/tests.yaml` files. The tox tool is installed as part of the development dependencies, so you can run the tests locally using the following command:

.. code-block:: console

    $ uv run tox --conf tests/config/tox.ini --root .

The GitHub Actions workflow can also be tested locally using the `act tool <https://nektosact.com/>`_, which can be installed by following the `official installation instructions <https://nektosact.com/installation/index.html>`_. After installing the act tool, you can run the GitHub Actions workflow locally using the following commands:

.. code-block:: console

    $ act             # To run all workflows
    $ act -j <job-id> # To run a single job with the specified job ID (e.g., unit-tests, build-documentation, pylint, etc.)

When first running act, it may ask you which Docker image to use. We recommend using the "full" image, although "medium" or even "micro" may also work. We have not tested this, however.

Our CI/CD pipeline will be run on your pull request. To ensure a successful review, please make sure that:

* All linters and static type checkers pass
* Unit tests pass for all supported Python versions (3.10-3.13)
* The documentation builds successfully

If any of these checks fail, we won't be able to accept the pull request.

5. Update the Documentation
---------------------------

If you have made any changes that affect the way the project is used, please ensure that the relevant sections of the documentation are updated. We use `Sphinx <https://www.sphinx-doc.org/en/master/>`_ to generate our documentation. The source files for the documentation can be found in the :repo:`docs/source` directory.

6. Update the Changelog
-----------------------

Don't forget to update the changelog with the changes you have made (:repo:`CHANGELOG.md`).

7. Add Yourself to the Contributors List
----------------------------------------

Please add yourself to the contributors list (:repo:`CONTRIBUTORS.md`). This is of course optional and you may choose to add yourself under a pseudonym.

8. Commit Your Changes
----------------------

Try to make few meaningful coherent commits with expressive commit messages. We follow the widely accepted 50/72 rule with a short subject line that is capped at 50 characters followed by a detailed description with lines capped at 72 characters, separated from the subject line by a blank line. After each commit, please ensure the repository remains in a working state. If the main branch has progressed since you branched it off, please use a rebase instead of a merge to avoid unnecessary merge commits.

9. Make a Pull Request
----------------------

Push your changes to your fork and create a pull request against the main repository. Please provide a detailed description of your changes and reference the issue you are addressing. We will review your changes as soon as possible.
