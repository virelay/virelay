"""Contains the command line interface for the VISPR application."""

import atexit
import argparse

from .server import Server
from .model import Workspace


class Application:
    """Represents the command line interface for the VISPR application."""

    def __init__(self):
        """Initializes a new Application instance."""

        # Initializes the command line argument parser
        self.argument_parser = argparse.ArgumentParser(
            prog="vispr_vnext",
            description="The vNext version of the visualization tool VISPR."
        )
        self.argument_parser.add_argument(
            'project',
            type=str,
            nargs='+',
            help='The project file that is to be loaded into the workspace. Multiple project files can be specified.'
        )

        # Initializes the workspace, which will contain all the loaded projects
        self.workspace = Workspace()

    def run(self):
        """Runs the application."""

        # Parses the command line arguments
        arguments = self.argument_parser.parse_args()

        # Adds the projects to the
        for project_path in arguments.project:
            self.workspace.add_project(project_path)

        # Registers the cleanup method, which will be called when the application is quit (the FLASK server is long
        # running and will only exit when the user sends a signal, e.g. via Ctrl+C, to stop the process, atexit
        # registers a callback, which is exected, when the Python interpreter is shut down)
        atexit.register(self.shutdown)

        # Creates the FLASK server, which serves the frontend website as well as the RESTful API
        server = Server(self.workspace)
        server.run()

    def shutdown(self):
        """Is invoked, when the application is shut down. Cleans up all resources acquired."""

        self.workspace.close()
