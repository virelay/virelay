"""Contains the command line interface for the VISPR application."""

import argparse

from .model import Workspace


class Application:
    """Represents the command line interface for the VISPR application."""

    def __init__(self):
        """Initializes a new application."""

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

        print(self.workspace.get_current_project().dataset[0])
        print(self.workspace.get_current_project().dataset[3:5])
        print(self.workspace.get_current_project().dataset[(0, 4, 5)])

        # When application exits, the workspace is closed
        self.workspace.close()
