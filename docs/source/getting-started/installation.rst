============
Installation
============

To get started, you first have to install ViRelAy on your system. The easiest way to install ViRelAy is to use the package of the latest ViRelAy release available on PyPI, which can be easily installed using your favorite Python package manager, e.g., ``pip``:

.. code-block:: console

   $ pip install virelay

You can then run ViRelAy using the following command:

.. code-block:: console

   $ virelay <project-file> [<project-file> ...]

If you'd like to try out the bleeding-edge development version or experiment with the included examples, you can also clone the Git repository and install it manually. The project uses the Python package and project manager `uv <https://github.com/astral-sh/uv>`_. You can find instructions on how to install and use uv in the `official documentation <https://docs.astral.sh/uv/>`_. To install the development version of ViRelAy and run it, you can use the following commands:

.. code-block:: console

   $ git clone https://github.com/virelay/virelay.git
   $ cd virelay
   $ uv sync
   $ uv run virelay <project-file> [<project-file> ...]
