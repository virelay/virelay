===========================
Using ViRelAy With Gunicorn
===========================

As described in the :doc:`../getting-started/basic-usage` and :doc:`features` articles, ViRelAy provides a command-line interface to serve the web application using a simple built-in HTTP server. While this built-in server is suitable for small projects and testing purposes, it may not provide the performance and scalability required for larger-scale deployments, such as required when installing ViRelAy on a remote server for collaborative work.

To unlock faster performance and scalability, we recommend running ViRelAy with `Gunicorn <https://gunicorn.org/>`_, a WSGI-compliant HTTP server that provides robust features and configuration options. Gunicorn is installed alongside ViRelAy by default, but you can also install a specific version using ``pip install gunicorn``.

To start ViRelAy using Gunicorn, use the following command:

.. code-block:: console

    $ gunicorn \
        --workers 4 \
        --bind 127.0.0.1:8000 \
        "virelay.application:run_wsgi_app(projects=['path/to/project-1.yaml', 'path/to/project-2.yaml'])"

This command starts the Gunicorn server with the following settings:

* ``--workers 4`` -- Runs four worker processes to handle incoming requests.
* ``--bind 127.0.0.1:8000`` -- Binds the server to 127.0.0.1 on port 8000.
* ``virelay.application:run_wsgi_app(projects=[...])"`` -- Starts ViRelAy in a WSGI-compatible mode. The ``projects`` argument instructs ViRelAy to loads two projects, ``project-1.yaml`` and ``project-2.yaml``.

You can specify multiple projects by passing a list of project paths as shown above. Alternatively, you can set the ``VIRELAY_PROJECTS`` environment variable to a colon-separated list of project paths:

.. code-block:: console

    $ export VIRELAY_PROJECTS="path/to/project-1.yaml:path/to/project-2.yaml"
    $ gunicorn \
        --workers 4 \
        --bind 127.0.0.1:8000 \
        "virelay.application:run_wsgi_app()"

Note that passing the projects explicitly to ``run_wsgi_app()`` takes precedence over the environment variable, i.e., if you use ``run_wsgi_app(projects=[...])``, ``VIRELAY_PROJECTS`` is ignored.
