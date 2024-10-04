========
Frontend
========

ViRelAy consists of 2 parts: the backend REST API and the frontend website. This article describes the architecture of the frontend in detail. The frontend is implemented in `TypeScript <https://www.typescriptlang.org/>`_ using `Angular <https://angular.io/>`_ and `Clarity <https://clarity.design/>`_. Angular applications are built with components, which define areas of responsibility in the UI. Components can then be re-used in other components just like regular HTML tags. Clarity is a design system, which provides ready-made Angular components for its UI components.

The source code of the frontend can be found in the :repo:`source/frontend/src` directory. This directory contains the following files and directories, which are important for development:

- ``main.ts`` -- The entrypoint to the Angular application.
- ``polyfills.ts`` -- Some polyfills that are needed to make certain required modern functionality work in older browsers.
- ``style.scss`` -- The main CSS styles that are available to the entire Angular application. The ViRelAy frontend writes its styles in SCSS, which is a CSS like language frontend for `SASS <https://sass-lang.com/>`_.
- ``index.html`` -- The index page, which contains the skeleton of the HTML view of the Angular application.
- ``services`` -- Services are a category of Angular building blocks, which usually serve a specific well-defined purpose. In the case of ViRelAy, each service represents the communication abstraction for a single backend REST API endpoint (projects, datasets, attributions, color maps, and analyses).
- ``environments`` -- Contains the configuration of the frontend application for different environments.
- ``assets`` -- Contains assets such as images.
- ``app`` -- The ``app`` directory contains the actual application code, which is subdivided into the following parts:

  - ``modules`` -- Angular components are grouped into modules, which can be imported into other modules to make components available across modules. The modules directory contains all major modules and their components, including the pages.
  - ``components`` -- This directory contains all components that are not page-specific and can thus be used across multiple pages. Currently, this only contains the embedding viewer component.
  - ``app.module.ts`` -- The app module is the root module of all modules in the application.
  - ``app.component.*`` -- The app component is the root component of all components, which gets bootstrapped by ``main.ts`` and loaded into the ``index.html`` page.

Development
===========

Before starting to work on the frontend, you need to install `Node.js <https://nodejs.org>`_, which is required for Angular. It is recommended to install an `active LTS or maintenance LTS release <https://nodejs.org/en/about/releases/>`_ of Node.js. After that, you can navigate to the frontend directory and install its dependencies like so:

.. code-block:: console

    $ cd source/frontend
    $ npm install

During development, the frontend can be started using the following command. This starts a development server, which re-compiles and reloads the application automatically when any source files are changed. Furthermore, this creates source maps for the compiled JavaScript files, which makes debugging much easier, as the TypeScript files can be used for debugging.

.. code-block:: console

    $ npx ng serve

For the frontend to properly work, the backend REST API must be started as well. The command line interface of the backend REST API offers a debug mode, which not only prints out helpful log messages to the console, but also puts the backend server into a mode where the frontend is not served through the backend. This is important for development, as the frontend is being served directly by the Angular CLI. The backend REST API can be started in debug mode using the following command:

.. code-block:: console

    $ uv run virelay '<project-file>' --debug-mode

Deployment
==========

Since the frontend is being served directly by the backend server when ViRelAy is started, a production version of the frontend is checked into the repository. Therefore, every time changes are made to the frontend, a production build has to be created using the following command:

.. code-block:: console

    $ npx ng build --configuration production

The ``--configuration production`` argument introduces optimizations for production the production build and also adds the hash of the build output to the file names, thus preventing the server from using older cached versions of the frontend. The frontend's static build output files are stored in :repo:`source/frontend/distribution` from where they are served by the backend server.
