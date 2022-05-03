===========================
Using ViRelAy With Gunicorn
===========================

As described in the :doc:`../getting-started/basic-usage` and :doc:`features` articles, ViRelAy provides a command line interface to serve the application using a simple built-in HTTP server. This HTTP server is, however, rather slow, because it is limited to responding to requests in sequence. To unlock the full potential of ViRelAy or even run it on a remote server to collaborate with others, it is recommended to run ViRelAy using the WSGI HTTP server `Gunicorn <https://gunicorn.org/>`_. Gunicorn was installed together with ViRelAy, but if you want to use a specific version, it can also be installed from PyPI: ``pip install gunicorn``.

To start ViRelAy using Gunicorn, you can use the ``gunicorn`` command and tell it how to create a ViRelAy application, which can be done like so:

.. code-block:: console

    $ gunicorn \
        --workers 4 \
        --bind 127.0.0.1:8080 \
        "virelay.application:create_app(projects=['path/to/project-1.yaml', 'path/to/project-2.yaml'])"

With the above command, the server binds to 127.0.0.1 on port 8080 and uses 4 worker processes. ViRelAy will load the two projects ``project-1.yaml`` and ``project-2.yaml``. You can specify as many projects as you like. Alternatively, the environment variable ``VIRELAY_PROJECTS`` may be used to specify the project paths as a colon-separated list like so:

.. code-block:: console

    $ export VIRELAY_PROJECTS="path/to/project-1.yaml:path/to/project-2.yaml"
    $ gunicorn --workers 4 --bind 127.0.0.1:8080 "virelay.application:create_app()"

Passing the projects explicitly to ``create_app()`` takes precedence over the environment variable, i.e., if ``create_app(projects=...)`` is used, ``VIRELAY_PROJECTS`` is ignored.
