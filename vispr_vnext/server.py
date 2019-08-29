"""Represents the server of VISPR, which serves the website and contains the RESTful API."""

import os
import logging

import flask


class Server:
    """Represents the server of VISPR, which encapsulates the website and the RESTful API."""

    def __init__(self, workspace):
        """
        Initializes a new Server instance.

        Parameters
        ----------
            workspace: Workspace
                The workspace that contains the projects that are to be managed by the server.
        """

        # Stores the workspace for later reference
        self.workspace = workspace

        # Creates the FLASK application
        self.app = flask.Flask('VISPR')

        # Registers the routes with the FLASK application
        self.app.add_url_rule('/api/workspace', 'get_workspace', self.get_workspace)

    def run(self, host='localhost', port=8080, debug=False):
        """
        Starts the FLASK server and returns when the application has finished.

        Parameters
        ----------
            host: str
                The IP address at which the application should run. Defaults to localhost.
            port: int
                The port at which the application should run. Defaults to 8080.
            debug: bool
                Determines whether the application should run in debug mode or not. Defaults to False.
        """

        # If the application is not run in debug mode, then all FLASK and Werkzeug logs are suppressed to make the
        # console output a lot cleaner
        if not debug:
            logging.getLogger('werkzeug').disabled = True
            os.environ['WERKZEUG_RUN_MAIN'] = 'true'

        # Starts the FLASK application
        self.app.run(host, port, debug)

    def get_workspace(self):
        """
        Retrieves all the projects and their respective information from the workspace.

        Returns
        -------
            str
                Returns a JSON string containing the projects of the workspace.
        """

        projects = []
        for project_id, project_name in enumerate(self.workspace.get_project_names()):
            project = self.workspace.get_project(project_name)
            project_data = {
                'id': project_id,
                'name': project_name,
                'model': project.model,
                'dataset': project.dataset.name,
                'analysisMethods': []
            }
            for analysis_method_id, analysis_method_name in enumerate(project.get_analysis_methods()):
                project_data['analysisMethods'].append({
                    'id': analysis_method_id,
                    'name': analysis_method_name,
                    'categories': project.get_category_names_of_analysis_method(analysis_method_name),
                    'clusterings': project.get_clustering_names_from_analysis_method(analysis_method_name),
                    'embeddings': project.get_embedding_names_from_analysis_method(analysis_method_name)
                })
            projects.append(project_data)

        return flask.jsonify(projects)
