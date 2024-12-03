"""Contains the command-line interface for the ViRelAy application."""

import os
import atexit
import argparse

import flask

from virelay import __version__
from virelay.server import Server
from virelay.model import Workspace


def run_cli_app() -> None:
    """Runs the application with a command-line interface (CLI) using the built-in server."""

    # Initializes the command-line argument parser
    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="virelay",
        description="A tool for visualizing relevance analyses.",
    )
    argument_parser.add_argument(
        'project',
        type=str,
        nargs='+',
        help='The project file that is to be loaded into the workspace. Multiple project files can be specified.'
    )
    argument_parser.add_argument(
        '-H',
        '--host',
        dest='host',
        type=str,
        default='localhost',
        help='The name or IP address at which the server should run. Defaults to "localhost".'
    )
    argument_parser.add_argument(
        '-p',
        '--port',
        dest='port',
        type=int,
        default=8000,
        help='The port at which the server should run. Defaults to 8000.'
    )
    argument_parser.add_argument(
        '-d',
        '--debug-mode',
        dest='debug_mode',
        action='store_true',
        help='''
            Determines whether the application is run in debug mode. When the application is in debug mode, all Flask and Werkzeug logs are
            printed to stdout, Flask debugging is activated (Flask will print out the debugger PIN for attaching the debugger), and automatic
            reloading (when files change) is activated. Furthermore, the frontend of the application will not be served by Flask and instead has
            to be served externally (e.g. via ng serve).
        '''
    )
    argument_parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f'ViRelAy {__version__}',
        help='Prints the version of the ViRelAy application.'
    )

    # Initializes the workspace, which will contain all the loaded projects
    workspace: Workspace = Workspace()

    # Parses the command-line arguments
    arguments = argument_parser.parse_args()

    # Adds the projects to the workspace
    for project_path in arguments.project:
        workspace.add_project(project_path)

    # Registers the cleanup method, which will be called when the application is quit (the Flask server is long running and will only exit when
    # the user sends a signal, e.g. via Ctrl+C, to stop the process, atexit registers a callback, which is executed, when the Python interpreter
    # is shut down)
    atexit.register(workspace.close)

    # Creates the Flask server, which serves the frontend web app as well as the backend REST API
    server = Server(workspace, arguments.debug_mode)
    server.run(arguments.host, arguments.port)


def run_wsgi_app(projects: list[str] | None = None) -> flask.Flask:
    """Runs the application with the WSGI (Python Web Server Gateway Interface), which can be used by WSGI servers like Gunicorn.

    Args:
        projects (list[str] | None): List of project files to load into the workspace. Defaults to None.

    Raises:
        RuntimeError: If no neither the projects parameter nor the VIRELAY_PROJECTS environment variable contains any projects.

    Returns:
        flask.Flask: Returns the Flask application.
    """

    if projects is None:
        try:
            colon_separated_projects = os.environ['VIRELAY_PROJECTS']
            projects = colon_separated_projects.split(':')
        except KeyError as exception:
            raise RuntimeError(
                "No Projects specified. Specify by setting environment VIRELAY_PROJECTS=\"project1.yaml:project2.yaml\""
            ) from exception

    workspace = Workspace()
    for project_path in projects:
        workspace.add_project(project_path)

    server = Server(workspace)
    atexit.register(workspace.close)

    return server.app
