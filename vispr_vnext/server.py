"""Represents the server of VISPR, which serves the website and contains the RESTful API."""

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
        self.app.add_url_rule('/api/projects', 'get_projects', self.get_projects)

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

        self.app.run(host, port, debug)

    def get_projects(self):
        """
        Retrieves the projects of the workspace.

        Returns
        -------
            str
                Returns a JSON string containing the projects of the workspace.
        """

        projects = []
        for project_id, project_name in enumerate(self.workspace.get_project_names()):
            projects.append({
                'id': project_id,
                'name': project_name
            })

        return flask.jsonify(projects)
