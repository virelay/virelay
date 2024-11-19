================
Frontend Web App
================

The ViRelAy application is built around two core components: a backend REST API and a frontend web app. This section delves into the detailed architecture of the frontend web app.

The frontend is developed using `TypeScript <https://www.typescriptlang.org/>`_, `Angular <https://angular.io/>`_ and `Clarity <https://clarity.design/>`_, a renowned design system that offers pre-built UI components tailored for Angular applications.

The source code of the frontend can be found in the :repo:`source/frontend` directory. This directory contains the following files and directories:

* ``app`` -- Contains ``main.ts``, the primary entrypoint to the Angular application, as well as the app component, the HTML index file, and the route definitions.
* ``assets`` -- Contains images and the favicon.
* ``components`` -- Contains reusable Angular components such as the embedding viewer.
* ``config`` -- Contains the configuration of the web app for different environments (develop and production).
* ``pages`` -- Contains Angular components that represent the pages of the web app, such as the project page, which displays a single loaded project.
* ``services`` -- Contains services that interact with the backend REST API. There are separate services for each endpoint of the backend: projects, datasets, attributions, color maps, and analyses.
* ``styles`` -- Contains the main stylesheets of the web app, which are available to the entire Angular application. The ViRelAy frontend utilizes SCSS, which is a CSS like language frontend for `SASS <https://sass-lang.com/>`_, for its stylesheets.
* ``angular.json`` -- Configures the Angular CLI and compiler.
* ``package.json`` -- Contains the project dependencies and other metadata.
* ``tsconfig.json`` -- Configures the TypeScript compiler.

Development Environment Setup
=============================

To start frontend development, it is essential to install `Node.js <https://nodejs.org>`_, a prerequisite for Angular. We recommend installing an `active LTS or maintenance LTS release <https://nodejs.org/en/about/releases/>`_ of Node.js, which can be easily accomplished through the `Node Version Manager (nvm) <https://github.com/nvm-sh/nvm>`_. Once Node.js is installed, the following command can be used to install the dependencies:

.. code-block:: console

    $ npm --prefix source/frontend install

Subsequently, the frontend can be started using the following command. This will start a development server and establish a local development environment that automatically re-compiles and reloads the application upon any changes to source files, while also generating source maps for the compiled JavaScript code for enhanced debugging capabilities.

.. code-block:: console

    $ npm --prefix source/frontend run start

To ensure that the frontend properly works, the backend REST API must be started in debug mode using the following command. Debug mode enables log messages to be printed to the console and prevents the frontend from being served through the backend server. This is important for development, as the frontend is being served directly by the Angular CLI.

.. code-block:: console

    $ uv --directory source/backend run virelay '<project-file>' --debug-mode

Building the Frontend
=====================

The frontend application is automatically compiled when the backend REST API project is built. However, for manual compilation, use the following command:

.. code-block:: console

    $ npm --prefix source/frontend run build

This command compiles the frontend code in production mode, incorporating optimizations and appending a hash to the file names to prevent cached versions from being served by the server. The compiled frontend output can be found in :repo:`source/frontend/distribution/browser`.  If the backend REST API is run without the ``--debug-mode`` flag, this is the location from where the frontend is served. Therefore, the frontend must be build before running the backend REST API locally without the ``--debug-mode`` flag.

Linting
=======

The frontend web app adheres to a rigorous code style, which is enforced by utilizing tools like `ESLint <https://eslint.org/>`_, a JavaScript/TypeScript linter, `Stylelint <https://stylelint.io/>`_, a CSS/Sass linter, and `HTML-Validate <https://html-validate.org/>`_, an HTML linter. These checks are integral to identifying potential runtime bugs and ensuring the quality of our codebase. It is essential that contributors regularly run these tools and rectify any warnings that arise. Moreover, it is imperative to verify the absence of warnings before committing changes or creating pull requests. The linting process is integrated into our CI pipeline, which automatically runs upon the creation of a pull request. Any pull request resulting in a failed build will not be accepted.

To keep the configurations for `ESLint <https://eslint.org/>`_ and `Stylelint <https://stylelint.io/>`_ separate from the frontend project and together with the configurations of the other linters, they are wrapped in their own NPM packages: :repo:`tests/eslint` and :repo:`tests/stylelint` (neither of them supports configuration files that are not in the same directory as the NPM package that is being linted). The below commands install the dependencies for these packages. This is required to run the linters locally.

.. code-block:: console

    $ npm --prefix tests/eslint install
    $ npm --prefix tests/stylelint install

The configuration files for each tool are located in the :repo:`tests/config` directory:

* **ESLint**: :repo:`tests/eslint/eslint.config.mjs`
* **Stylelint**: :repo:`tests/stylelint/.stylelintrc.mjs`
* **HTML-Validate**: :repo:`tests/config/.htmlvalidate.js`

The easiest way to run the linters is through NPM, which can be achieved using the following commands:

.. code-block:: console

    $ npm --prefix source/frontend run eslint
    $ npm --prefix source/frontend run stylelint
    $ npm --prefix source/frontend run html-validate

Alternatively, the linters can be executed manually:

.. code-block:: console

    $ npx --prefix source/frontend eslint \
        --config source/frontend/eslint.config.mjs \
        'source/frontend/**/*.{ts,mjs}'

    $ npx --prefix source/frontend stylelint \
        --config tests/stylelint/.stylelintrc.mjs ß
        'source/frontend/**/*.scss'

    $ npx --prefix source/frontend html-validate \
        --config tests/config/.htmlvalidate.js \
        'source/frontend/!(node_modules)/**/*.html'

.. note::

    If you use Visual Studio Code and the `HTML-Validate extension <https://marketplace.visualstudio.com/items?itemName=html-validate.vscode-html-validate>`_, you need to symlink the configuration file to the root of the workspace, as the extension does not support configuration files in sub directories. This can be done by running the following command:

    .. code-block:: console

        $ ln -s tests/config/.htmlvalidate.js .htmlvalidate.js

    The symlink is already ignored in the :repo:`.gitignore` file, so that it is not committed to the repository.
