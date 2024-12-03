=======================
Contributing to ViRelAy
=======================

ViRelAy is an open-source project that relies on the contributions of its community, and we are excited to have you join us. Your enthusiasm and support are essential to our success, and we encourage you to participate in various ways.

There are numerous opportunities to contribute to ViRelAy, including:

* Filing bug reports or feature requests
* Updating documentation
* Contributing code to the project

To begin contributing, we recommend starting with a thorough understanding of the project. We suggest reviewing our user guide :doc:`../user-guide/index` for a surface-level introduction to the application and its features. The :doc:`index` contains comprehensive resources to provide you with valuable insights into how ViRelAy works internally, such as the :doc:`database-specification` and the :doc:`project-file-format`.

ViRelAy consists of two primary components:

* **Backend REST API** -- Written in Python using `Flask <https://flask.palletsprojects.com/en/stable/>`_, this part provides the foundation for our system's functionality.
* **Frontend** -- Developed using `Angular <https://angular.io/>`_ and `Clarity <https://clarity.design/>`_, the frontend delivers a user-friendly interface.


To delve deeper into each component, we recommend reviewing the in-depth articles on the :doc:`backend-rest-api` and the :doc:`frontend`.

Reporting Issues & Feature Requests
===================================

If you encounter a bug or have a feature request, we encourage you to submit an issue on our `GitHub page <https://github.com/virelay/virelay/issues>`_. Before creating a new issue, please review existing issues to avoid duplicate efforts and ensure that your report adds value. If you find an open issue related to the same problem, feel free to contribute additional information or context to help us resolve it more efficiently.

When submitting a new issue, provide as much relevant information as possible to facilitate prompt identification and resolution of the problem. This includes:

* Operating system details (e.g., Windows 11, macOS 15, Ubuntu 24.04)
* ViRelAy version you are using
* Any pertinent configuration settings or dependencies

Also, please provide a clear, step-by-step guide on how to reproduce the issue. This will enable us to diagnose and fix the problem more quickly. If possible, including a minimal example that reproduces the issue (i.e., a project file, dataset, label map, attributions, and analysis results) is highly appreciated.

Contributing Code or Documentation
==================================

Before contributing code or documentation, please ensure that there is no existing issue that aligns with your ideas. This helps avoid duplication of effort and ensures a seamless integration of your contributions into the project. If you have an idea for a contribution but can't find a related issue, we encourage you to open an issue before starting you work, where you outline your proposal. This facilitates alignment with the rest of the team and may prevent unnecessary work.

To contribute code or documentation, follow these steps:

1. Fork the Repository
----------------------

To begin contributing to this project, you will first need to `fork the repository on GitHub <https://github.com/virelay/virelay/fork>`_. This creates a copy of the original repository under your own account. Once you have cloned your fork, please create a new branch specifically for your feature or bug fix. When naming your branch, we recommend using kebab-case (lowercase words separated by hyphens) to clearly describe its purpose, e.g., ``my-new-feature``.

2. Make your Changes
--------------------

To contribute to this project, please make the necessary changes to the codebase while adhering to our established coding standards and guidelines. We recommend extensively documenting your code with comments. For the backend API we follow the `Google-style Docstring <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_ convention and the `JSDoc <https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html>`_ convention for frontend.

When modifying existing code, please refrain from altering the project's coding style unless absolutely necessary. Changes to the code style can lead to unnecessary effort and frequent updates to accommodate varying preferences. To ensure consistency and maintainability, we utilize various tools to enforce our coding conventions, detect potential issues, prevent bugs, and statically type-check the backend REST API:

* `PyLint <https://www.pylint.org/>`_ -- Enforces coding style and detects potential issues and bugs.
* `PyCodeStyle <https://pycodestyle.pycqa.org/en/latest/intro.html>`_ -- Verifies code style consistency.
* `PyDocLint <https://jsh9.github.io/pydoclint/>`_ -- Ensures proper documentation and adherence to Docstring style guidelines.
* `MyPy <https://mypy-lang.org/>`_ -- Statically type-checks the backend REST API.

Before committing your changes, please verify that none of these tools produce warnings. Additionally, we advise against modifying the configuration of these tools unless a compelling reason exists (please provide details on your reasoning in the accompanying issue or pull request).

3. Write Unit Tests
-------------------

To ensure the reliability and stability of our codebase, please write comprehensive unit tests for the features you have added. Our goal is to achieve 100% test coverage for the backend REST API. Although we do not currently maintain a test suite for the frontend, we encourage you to follow best practices and write tests where feasible.

Before committing your changes, please ensure that all unit tests pass without errors or failures. This ensures that our codebase remains robust and maintains its expected functionality.

4. Update the Documentation
---------------------------

If your changes have impacted how the project is used or you made changes to its functionality, please ensure that the relevant sections of our documentation are updated accordingly. We use `Sphinx <https://www.sphinx-doc.org/en/master/>`_ to generate our documentation, which can be found in the :repo:`docs/source` directory.

A local build of the documentation can be created using the following command:

.. code-block:: console

    $ uv run --directory source/backend tox --conf ../../tests/config/tox.ini -e docs

5. Testing & Linting
--------------------

We use tox to run unit tests, linters and static type checkers on the backend REST API, as well as to build the documentation. If you've made any changes to the backend REST API or the documentation that require updates to configurations of the linters, type checker, or tox, please ensure that the relevant sections in the following configuration files are are revised accordingly:

* **tox**: :repo:`tests/config/tox.ini`
* **PyLint**: :repo:`tests/config/pylint.ini`
* **PyCodeStyle**: :repo:`tests/config/.pycodestyle`
* **PyDocLint**: :repo:`tests/config/.pydoclint.toml`
* **MyPy**: :repo:`tests/config/.mypy.ini`

To run tests and build the documentation locally using tox, execute the following command from the project root:

.. code-block:: console

    $ uv --directory source/backend run tox --conf ../../tests/config/tox.ini run

To check the code quality of the frontend web app, we also use a range of linters, which can be run using the following commands:

.. code-block:: console

    $ npm --prefix source/frontend run eslint
    $ npm --prefix source/frontend run stylelint
    $ npm --prefix source/frontend run html-validate

If your changes require updates to the configurations of the frontend linters, please update the following configuration files:

* **ESLint**: :repo:`tests/eslint/eslint.config.mjs`
* **Stylelint**: :repo:`tests/stylelint/.stylelintrc.mjs`
* **HTML-Validate**: :repo:`tests/config/.htmlvalidate.js`

Finally, we use a Markdown linter to ensure the quality of the read me and a spell checker to verify the correct spelling of all text, including code files. The Markdown linter and the spell checker can be run using the following commands:

.. code-block:: console

    $ npm --prefix tests/markdownlint run markdownlint
    $ npm --prefix tests/cspell run cspell

If your changes require updates to the configurations of the Markdown linter or the spell checker, please update the following configuration files:

* **Markdown Linter**: :repo:`tests/markdownlint/.markdownlint.yaml`
* **Spell Checker**: :repo:`tests/cspell/.cspell.json`

Our continuous integration and deployment (CI/CD) pipeline is built using GitHub Actions Workflows. You can use the `act tool <https://nektosact.com/>`_ to test the GitHub Actions workflow locally. Install the act tool according to the `official installation instructions <https://nektosact.com/installation/index.html>`_. After the installation, the GitHub Actions workflow can be run locally using the following commands:

.. code-block:: console

    $ act                # Runs all workflows
    $ act --job <job-id> # Runs a single job with the specified ID (e.g., unit-tests, build-documentation, pylint, etc.)

When prompted to select a Docker image, we recommend using the "full" image.

If your changes require updates to the GitHub Actions workflows, please update the following configuration file: :repo:`.github/workflows/tests.yaml`.

To ensure a successful review of your pull request, please verify that:

* All linters and static type checkers pass without errors.
* Unit tests succeed for all supported Python versions (3.10 - 3.13).
* The documentation builds successfully.

If any of these checks fail, we will not be able to accept the pull request.


6. Update the Changelog
-----------------------

As part of your contribution, please ensure that the project's changelog is updated to reflect the modifications you've made. This can be done by editing the :repo:`CHANGELOG.md` file.

By recording your changes in our changelog, we can maintain a clear and accurate history of updates, making it easier for users and developers to track progress and understand the impact of each release.

7. Add Yourself to the Contributors List
----------------------------------------

As a final step before committing your changes and making a pull request, please consider adding your name to our contributors list in :repo:`CONTRIBUTORS.md`. This allows us to formally recognize and appreciate your contribution to the project.

You may choose to add yourself under a pseudonym or use your actual name; we respect your preference and encourage you to acknowledge your hard work in making this project better.

8. Commit Your Changes
----------------------

To ensure that your contributions are easily reviewable and maintainable, please strive for a few meaningful, coherent commits with descriptive commit messages. We follow the conventional 50/72 rule:

* A brief subject line (not exceeding 50 characters) that summarizes the changes.
* A detailed description (with lines capped at 72 characters), separated from the subject line by a blank line.

Additionally, after each commit, please ensure that the repository remains in a healthy state. If the main branch has progressed since you branched it off, use a Git rebase instead of a merge to avoid unnecessary merge commits. This helps keep the commit history clean and makes it easier for others to review your changes.

9. Submit Your Contribution for Review
--------------------------------------

Once you've completed your development work, push your changes to your forked repository and create a pull request against the main repository. When creating the pull request, please provide a clear and detailed description of your changes, including how they address the specific issue or feature being implemented.

Be sure to reference the relevant issues in your description so that our review team can easily identify the context for your contribution. We'll strive to review your submission as soon as possible, providing feedback and guidance to ensure a smooth integration process.
