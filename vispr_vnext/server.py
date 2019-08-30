"""Represents the server of VISPR, which serves the website and contains the RESTful API."""

import os
import logging
import traceback

import numpy
import flask


class Server:
    """Represents the server of VISPR, which encapsulates the website and the RESTful API."""

    def __init__(self, workspace, is_in_debug_mode=False):
        """
        Initializes a new Server instance.

        Parameters
        ----------
            workspace: Workspace
                The workspace that contains the projects that are to be managed by the server.
            is_in_debug_mode: bool
                Determines whether the application should run in debug mode or not. Defaults to False.
        """

        # Stores the arguments for later reference
        self.workspace = workspace
        self.is_in_debug_mode = is_in_debug_mode

        # Creates the FLASK application
        self.app = flask.Flask('VISPR')

        # Registers the routes with the FLASK application
        self.app.add_url_rule(
            '/api/workspace',
            'get_workspace',
            self.get_workspace
        )
        self.app.add_url_rule(
            '/api/projects/<int:project_id>/analyses/<string:analysis_method_name>',
            'get_analysis',
            self.get_analysis
        )
        self.app.add_url_rule(
            '/api/projects/<int:project_id>/attributions/<int:attribution_index>',
            'get_attribution',
            self.get_attribution
        )
        self.app.add_url_rule(
            '/api/projects/<int:project_id>/dataset/<int:sample_index>',
            'get_sample',
            self.get_sample
        )

    def run(self, host='localhost', port=8080):
        """
        Starts the FLASK server and returns when the application has finished.

        Parameters
        ----------
            host: str
                The IP address at which the application should run. Defaults to localhost.
            port: int
                The port at which the application should run. Defaults to 8080.
        """

        # If the application is not run in debug mode, then all FLASK and Werkzeug logs are suppressed to make the
        # console output a lot cleaner
        if not self.is_in_debug_mode:
            logging.getLogger('werkzeug').disabled = True
            os.environ['WERKZEUG_RUN_MAIN'] = 'true'

        # Starts the FLASK application
        self.app.run(host, port, self.is_in_debug_mode)

    def get_workspace(self):
        """
        Retrieves all the projects and their respective information from the workspace.

        Returns
        -------
            flask.Response
                Returns an HTTP 200 OK response with a JSON string as content that contains the projects of the
                workspace as well as their information.
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

            for analysis_method_name in project.get_analysis_methods():
                project_data['analysisMethods'].append({
                    'name': analysis_method_name.replace('_', '-'),
                    'categories': project.get_analysis_category_names(analysis_method_name),
                    'clusterings': project.get_analysis_clustering_names(analysis_method_name),
                    'embeddings': project.get_analysis_embedding_names(analysis_method_name)
                })

            projects.append(project_data)

        return self.http_ok(projects)

    def get_sample(self, project_id, sample_index):
        """
        Retrieves the dataset sample with the specified index from the specified project.

        Parameters
        ----------
            project_id: int
                The ID of the project from which the dataset sample is to be retrieved.
            sample_index: int
                The index of the dataset sample that is to be retrieved.

        Returns
        -------
            Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the dataset
            sample.
            If the specified project does not exist, then an HTTP 404 Not Found response is returned.
            If the specified dataset sample does not exist, then an HTTP 404 Not Found response is returned.
        """

        # Checks if a project with the specified ID exists
        if project_id >= len(self.workspace.projects):
            return self.http_not_found('The project with the ID {0} could not be found.'.format(project_id))
        project = self.workspace.get_project(self.workspace.get_project_names()[project_id])

        # Retrieves the dataset sample with the specified index
        try:
            sample = project.get_sample(sample_index)
        except LookupError as error:
            return self.http_not_found(error)

        # Returns the retrieved dataset sample
        return self.http_ok({
            'index': sample.index,
            'labels': sample.labels
        })

    def get_attribution(self, project_id, attribution_index):
        """
        Retrieves the attribution with the specified index from the specified project.

        Parameters
        ----------
            project_id: int
                The ID of the project from which the attribution is to be retrieved.
            attribution_index: int
                The index of the attribution that is to be retrieved.

        Returns
        -------
            Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the attribution.
            If the specified project does not exist, then an HTTP 404 Not Found response is returned.
            If the specified attribution does not exist, then an HTTP 404 Not Found response is returned.
        """

        # Checks if a project with the specified ID exists
        if project_id >= len(self.workspace.projects):
            return self.http_not_found('The project with the ID {0} could not be found.'.format(project_id))
        project = self.workspace.get_project(self.workspace.get_project_names()[project_id])

        # Retrieves the attribution with the specified index
        try:
            attribution = project.get_attribution(attribution_index)
        except LookupError as error:
            return self.http_not_found(error)

        # Returns the retrieved attribution
        return self.http_ok({
            'index': attribution.index,
            'labels': attribution.labels,
            'prediction': numpy.array(attribution.prediction).tolist()
        })

    def get_analysis(self, project_id, analysis_method_name):
        """
        Retrieves the analysis from the specified project with the specified analysis method. Besides the project ID and
        the analysis method name, the name of the category, clustering, and embedding have to be specified as URL
        parameters.

        Parameters
        ----------
            project_id: int
                The ID of the project from which the analysis is to be retrieved.
            analysis_method_name: str
                The name of the analysis method from which the analysis is to be retrieved.

        Returns
        -------
            flask.Response
                Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the analysis.
                If the specified project does not exist, then an HTTP 404 Not Found response is returned.
                If the specified analysis method does not exist, then an HTTP 404 Not Found response is returned.
                If the analysis does not exist, then an HTTP 404 Not Found response is returned.
                If no category name, clustering name, or embedding name were specified in the URL parameters, then an
                HTTP 400 Bad Request response is returned.
        """

        # Checks if a project with the specified ID exists
        if project_id >= len(self.workspace.projects):
            return self.http_not_found('The project with the ID {0} could not be found.'.format(project_id))
        project = self.workspace.get_project(self.workspace.get_project_names()[project_id])

        # Checks if the specified analysis method exists
        analysis_method_name = analysis_method_name.replace('-', '_')
        if analysis_method_name not in project.get_analysis_methods():
            return self.http_not_found('The specified analysis method "{0}" could not be found.'.format(
                analysis_method_name.replace('_', '-')
            ))

        # Retrieves the other parameters from the URL, if one is missing, an HTTP Bad Request response is returned
        category_name = flask.request.args.get('category')
        if category_name is None:
            return self.http_bad_request('No category was specified.')
        clustering_name = flask.request.args.get('clustering')
        if clustering_name is None:
            return self.http_bad_request('No clustering was specified.')
        embedding_name = flask.request.args.get('embedding')
        if embedding_name is None:
            return self.http_bad_request('No embedding was specified.')

        # Gets the specified analysis
        try:
            analysis = project.get_analysis(analysis_method_name, category_name, clustering_name, embedding_name)
        except LookupError as error:
            return self.http_not_found(error)

        # The analysis consists mainly of three lists: one that contains the embedding array, one that contains the
        # index of the attribution to which the analysis belongs, and one that contains the cluster of the embeddings,
        # this may be convenient in Python, but it is not in JavaScript, so these three lists are combined into a single
        # list containing the embeddings as objects
        clustering = numpy.array(analysis.clustering).tolist()
        embedding = numpy.array(analysis.embedding).tolist()
        indices = numpy.array(analysis.indices).tolist()
        zipped_embedding = []
        for index, sample_embedding in enumerate(embedding):
            zipped_embedding.append({
                'cluster': clustering[index],
                'attributionIndex': indices[index],
                'value': sample_embedding
            })

        # Returns the retrieved analysis
        return self.http_ok({
            'categoryName': analysis.category_name,
            'humanReadableCategoryName': analysis.human_readable_category_name,
            'clusteringName': analysis.clustering_name,
            'embeddingName': analysis.embedding_name,
            'embedding': zipped_embedding
        })

    def http_ok(self, content):
        """
        Generates an HTTP 200 OK response.

        Parameters
        ----------
            content
                The content that is to be converted into JSON and returned in the body of the response.

        Returns
        -------
            flask.Response
                Returns an HTTP 200 OK response.
        """

        response = flask.jsonify(content)
        response.status_code = 200
        return response

    def http_bad_request(self, error_message):
        """
        Generates an HTTP 400 Bad request response.

        Parameters
        ----------
            error_message: str
                The error message that is to be returned in the body of the response.

        Returns
        -------
            flask.Response
                Returns an HTTP 400 Bad Request response.
        """

        if isinstance(error_message, BaseException):
            error_message = self.format_exception(error_message)

        response = flask.jsonify({'errorMessage': str(error_message)})
        response.status_code = 400
        return response

    def http_not_found(self, error_message):
        """
        Generates an HTTP 404 Not Found response.

        Parameters
        ----------
            error_message: str
                The error message that is to be returned in the body of the response.

        Returns
        -------
            flask.Response
                Returns an HTTP 404 Not found response.
        """

        if isinstance(error_message, BaseException):
            error_message = self.format_exception(error_message)

        response = flask.jsonify({'errorMessage': str(error_message)})
        response.status_code = 404
        return response

    def format_exception(self, exception):
        """
        Formats the specified exception as a string so that it can be logged.

        Parameters
        ----------
            exception: BaseException
                The exception that is to be formatted.

        Returns
            str
                Returns a string, which contains the error message of the exception. If the server is being run in debug
                mode, then the traceback is also included in the string that is returned.
        """

        error_message = str(exception)
        if self.is_in_debug_mode:
            error_message = '{0}\n{1}'.format(
                error_message,
                '\n'.join(traceback.format_tb(exception.__traceback__))
            )
        return error_message
