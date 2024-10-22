============
Installation
============

To get started, you first have to install ViRelAy on your system. The recommended and easiest way to install ViRelAy is to use `pipx <https://pipx.pypa.io>`_, which is a tool for installing Python applications from the `Python package index (PyPI) <https://pypi.org/>`_ in isolated environments:

.. code-block:: console

   $ pipx install virelay

You can then run ViRelAy using the following command:

.. code-block:: console

   $ virelay <project-file> [<project-file> ...]

Alternatively, you can also install ViRelAy using `pip <https://pip.pypa.io>`_, although it is recommended to create a virtual environment to avoid conflicts with other Python packages:

.. code-block:: console

   $ python3 -m venv virelay-env
   $ source virelay-env/bin/activate
   $ pip install virelay
   $ virelay <project-file> [<project-file> ...]

If you'd like to try out the bleeding-edge development version or experiment with the included examples, you can also clone the Git repository and install it manually. The project uses the Python package and project manager `uv <https://github.com/astral-sh/uv>`_. You can find instructions on how to install and use uv in the `official documentation <https://docs.astral.sh/uv/>`_. To install and run the development version of ViRelAy and run it, you can use the following commands:

.. code-block:: console

   $ git clone https://github.com/virelay/virelay.git
   $ cd virelay
   $ uv --directory source/backend sync
   $ uv --directory source/backend run virelay <project-file> [<project-file> ...]
