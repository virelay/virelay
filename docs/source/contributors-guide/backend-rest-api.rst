================
Backend REST API
================

The backend server can be run using the following command (assuming you installed a virtual environment as described above):

.. code-block:: console

    $ .venv/bin/python -m virelay --debug-mode <project-file> [<project-file>, ...]

The ``--debug-mode`` flag starts the backend server in debug mode, which prints out detailed server logs, starts FLASK in debug mode (FLASK will print out a debugger pin that can be used to attach a debugger), activates auto-reload when files have changed, and will not serve the frontend via FLASK. This way, the frontend and backend can be worked on independent from each other.
