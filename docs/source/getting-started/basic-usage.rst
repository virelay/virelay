===========
Basic Usage
===========

If you already have a project file that you want to open, ViRelAy it can be started on the command line using the following command. If you do not have a project file, yet, you can read the :doc:`example-project` article, which guides you through the creation of a randomly generated project that you can use to familiarize yourself with the ViRelAy user interface.

.. code-block:: console

    python -m virelay <project-file> [<project-file>, ...]

This will start the server at http://localhost:8080 and automatically open your default browser. Optionally, you can specify an alternative host and port using the ``--host`` and ``--port`` command line arguments.

Please note, that starting ViRelAy using the command line interface is very easy, but it will start a rather slow development server. For improved load times or when running ViRelAy on a server, please run it using the WSGI HTTP server Gunicorn. For more information, please refer to :doc:`../user-guide/using-virelay-with-gunicorn`.

After launching ViRelAy, you will be greeted with a user interface like in the following screenshot (the exact setup will depend on the project(s) that you have loaded):

.. figure:: ../../images/virelay-screenshot.png
    :alt: Screenshot of the ViRelAy UI
    :align: center

    Figure1: A screenshot of the ViRelAy user interface.
