===========================
Using ViRelAy With Gunicorn
===========================

As described in the :doc:`../getting-started/basic-usage` and :doc:`features` articles, ViRelAy provides a command line interface to serve the web application using a simple built-in HTTP server. While the built-in HTTP server is convenient for development purposes, it can be slow and limiting for larger-scale applications. To unlock faster performance and scalability, for example when running ViRelAy on a server to collaborate with others, we recommended running ViRelAy with the WSGI HTTP server `Gunicorn <https://gunicorn.org/>`_. Gunicorn was installed together with ViRelAy, but if you want to use a specific version, it can also be installed from PyPI: ``pip install gunicorn``.

To start ViRelAy using Gunicorn, use the following command:

.. code-block:: console

    $ gunicorn \
        --workers 4 \
        --bind 127.0.0.1:8080 \
        "virelay.application:create_app(projects=['path/to/project-1.yaml', 'path/to/project-2.yaml'])"

With the above command, the server binds to 127.0.0.1 on port 8080 and uses 4 worker processes. ViRelAy will load the two projects ``project-1.yaml`` and ``project-2.yaml``. You can specify as many projects as you like. Alternatively, you can use the ``VIRELAY_PROJECTS`` environment variable to specify the project paths as a colon-separated list:

.. code-block:: console

    $ export VIRELAY_PROJECTS="path/to/project-1.yaml:path/to/project-2.yaml"
    $ gunicorn --workers 4 --bind 127.0.0.1:8080 "virelay.application:create_app()"

Note that passing the projects explicitly to `create_app()` takes precedence over the environment variable, i.e., if ``create_app(projects=...)`` is used, `VIRELAY_PROJECTS` is ignored.
