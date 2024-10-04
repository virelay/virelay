"""Represents the server of ViRelAy, which serves the website and contains the RESTful API."""

import io
import logging
import traceback
import threading
import webbrowser
from importlib.resources import files
from typing import Any, BinaryIO, cast

import numpy
import flask
import flask_cors
from PIL import Image
from numpy.typing import NDArray
from flask.typing import RouteCallable
from typing_extensions import TypedDict, NotRequired

from virelay.model import Workspace
from virelay.image_processing import render_heatmap


class Server:
    """Represents the server of ViRelAy, which encapsulates the website and the RESTful API."""

    def __init__(self, workspace: Workspace, is_in_debug_mode: bool = False) -> None:
        """Initializes a new Server instance.

        Args:
            workspace (Workspace): The workspace that contains the projects that are to be managed by the server.
            is_in_debug_mode (bool): Determines whether the application should run in debug mode or not. Defaults to False. When the application is in
                debug mode, then all Flask and Werkzeug logs are printed to stdout, Flask debugging is activated (Flask will print out the debugger
                PIN for attaching the debugger), and the automatic reloading, when the Python files change is activated. Furthermore, the frontend of
                the application will not be served via the. Otherwise all these things will be deactivated and the frontend of the application is
                served via the Flask server. If the application is to be debugged using Visual Studio Code (or any other IDE for that matter), then
                the application must not be started in debug mode, because Visual Studio will create its own debugger.
        """

        # Stores the arguments for later reference
        self.workspace: Workspace = workspace
        self.is_in_debug_mode: bool = is_in_debug_mode

        # Initializes the class members
        self.color_maps: dict[str, str] = {
            'gray-red': 'Gray Red',
            'black-green': 'Black Green',
            'black-fire-red': 'Black Fire-Red',
            'black-yellow': 'Black Yellow',
            'blue-white-red': 'Blue White Red',
            'afm-hot': 'AFM Hot',
            'jet': 'Jet',
            'seismic': 'Seismic'
        }

        # Creates the Flask application
        self.app: flask.Flask = flask.Flask('ViRelAy')

        # Registers the routes of the RESTful API with the Flask application
        self.app.add_url_rule(
            '/api/projects',
            'get_projects',
            self.get_projects
        )
        self.app.add_url_rule(
            '/api/projects/<int:project_id>',
            'get_project',
            self.get_project
        )
        self.app.add_url_rule(
            '/api/projects/<int:project_id>/dataset/<int:sample_index>',
            'get_sample',
            self.get_sample
        )
        self.app.add_url_rule(
            '/api/projects/<int:project_id>/dataset/<int:sample_index>/image',
            'get_sample_image',
            self.get_sample_image
        )
        self.app.add_url_rule(
            '/api/projects/<int:project_id>/attributions/<int:attribution_index>',
            'get_attribution',
            self.get_attribution
        )
        self.app.add_url_rule(
            '/api/projects/<int:project_id>/attributions/<int:attribution_index>/heatmap',
            'get_attribution_heatmap',
            self.get_attribution_heatmap
        )
        self.app.add_url_rule(
            '/api/projects/<int:project_id>/analyses/<string:analysis_method_name>',
            'get_analysis',
            self.get_analysis
        )
        self.app.add_url_rule(
            '/api/color-maps',
            'get_color_maps',
            self.get_color_maps
        )
        self.app.add_url_rule(
            '/api/color-maps/<string:color_map>',
            'get_color_map_preview',
            self.get_color_map_preview
        )

        # When the application is not in debug mode, then the Angular frontend is served via the static file serving feature in Flask; the
        # create_static_file_view_function and create_static_file_parameterized_view_function functions are used to create view functions for the
        # files that are to be served; otherwise specialized functions for each route would have to be created; these methods take a file path and
        # return a view function that returns the specified file; the un-parameterized version creates a view function that serves the specified file
        # directly, while the parameterized version creates a view function that serves a file with a file name that is specified as a parameter in
        # the URL, which is passed to the view function as an argument by Flask (when ViRelAy is run from the source code, then the frontend is
        # located in the source directory; if, however, ViRelAy is run from an installed package, then the frontend is included in the package)
        resources_path = files('virelay') / 'frontend'
        if not resources_path.is_dir():
            resources_path = files('frontend') / 'distribution'
        if not self.is_in_debug_mode:
            def create_static_file_view_function(relative_file_path: str) -> RouteCallable:
                def view_function() -> flask.Response:
                    file_path = resources_path / relative_file_path
                    file_stream: BinaryIO = cast(BinaryIO, file_path.open('rb'))
                    return flask.send_file(file_stream, download_name=file_path.name)
                return view_function

            def create_static_file_parameterized_view_function(file_path_template: str) -> RouteCallable:
                def view_function(file_name: str) -> flask.Response:
                    file_path = resources_path / file_path_template.format(file_name)
                    file_stream: BinaryIO = cast(BinaryIO, file_path.open('rb'))
                    return flask.send_file(file_stream, download_name=file_path.name)
                return view_function

            self.app.add_url_rule(
                '/',
                'serve_frontend_index',
                create_static_file_view_function('index.html')
            )
            self.app.add_url_rule(
                '/favicon.ico',
                'serve_frontend_favicon',
                create_static_file_view_function('favicon.ico')
            )
            self.app.add_url_rule(
                '/<string:file_name>.css',
                'serve_frontend_css',
                create_static_file_parameterized_view_function('{0}.css')
            )
            self.app.add_url_rule(
                '/<string:file_name>.js',
                'serve_frontend_javascript',
                create_static_file_parameterized_view_function('{0}.js')
            )
            self.app.add_url_rule(
                '/assets/images/<string:file_name>.png',
                'serve_frontend_assets',
                create_static_file_parameterized_view_function('assets/images/{0}.png')
            )
            self.app.add_url_rule(
                '/<path:file_name>',
                'serve_frontend_catch_all',
                create_static_file_parameterized_view_function('index.html')
            )

    def run(self, host: str = 'localhost', port: int = 8080) -> None:
        """Starts the Flask server and returns when the application has finished.

        Args:
            host (str): The IP address at which the application should run. Defaults to localhost.
            port (int): The port at which the application should run. Defaults to 8080.
        """

        # If the application is not run in debug mode, then all Flask and Werkzeug logs are suppressed to make the console output a lot cleaner
        if not self.is_in_debug_mode:
            logging.getLogger('werkzeug').disabled = True

        # When the application is not in debug mode, then the browser is automatically opened upon application startup (the problem is, that the Flask
        # app run() method is blocking, so we cannot start the browser when the app is run, so we have to set a timer, which will run on a different
        # thread and start the thread after the server, hopefully, has started)
        if not self.is_in_debug_mode:
            threading.Timer(1, lambda: webbrowser.open_new_tab(f'http://localhost:{port}')).start()

        # When the application is started in debug mode, then the frontend is not served from the same host and port, therefore CORS must be activated
        if self.is_in_debug_mode:
            flask_cors.CORS(self.app)

        # Starts the Flask application
        self.app.debug = self.is_in_debug_mode
        self.app.run(host, port, self.is_in_debug_mode)

    def get_projects(self) -> flask.Response:
        """Retrieves all the projects and their respective information from the workspace.

        Returns:
            flask.Response: Returns an HTTP 200 OK response with a JSON string as content that contains the projects of the workspace as well as their
                information.
        """

        projects_json: list[ProjectJson] = []
        for project_id, project_name in enumerate(self.workspace.get_project_names()):

            project = self.workspace.get_project(project_name)
            projects_json.append({
                'id': project_id,
                'name': project_name,
                'model': project.model,
                'dataset': project.dataset.name if project.dataset is not None else 'Unknown Dataset'
            })

        return http_ok(projects_json)

    def get_project(self, project_id: int) -> flask.Response:
        """Retrieves the project with the specified ID.

        Args:
            project_id (int): The ID of the project that is to be retrieved.

        Returns:
            flask.Response: Returns an HTTP 200 OK response with a JSON string as content, which contains the project information. If the specified
                project could not be found, then an HTTP 404 Not Found response is returned.
        """

        if project_id >= len(self.workspace.get_project_names()):
            return http_not_found(f'The project with the ID {project_id} could not be found.', self.is_in_debug_mode)

        project_name = self.workspace.get_project_names()[project_id]
        project = self.workspace.get_project(project_name)
        project_json: ProjectJson = {
            'id': project_id,
            'name': project_name,
            'model': project.model,
            'dataset': project.dataset.name if project.dataset is not None else 'Unknown Dataset',
            'analysisMethods': []
        }

        for analysis_method_name in project.get_analysis_methods():
            analysis_method_json: AnalysisMethodJson = {
                'name': analysis_method_name.replace('_', '-'),
                'clusterings': project.get_analysis_clustering_names(analysis_method_name),
                'categories': [],
                'embeddings': project.get_analysis_embedding_names(analysis_method_name)
            }
            for category in project.get_analysis_categories(analysis_method_name):
                analysis_method_json['categories'].append({
                    'name': category.name,
                    'humanReadableName': category.human_readable_name
                })
            if project_json['analysisMethods'] is not None:
                project_json['analysisMethods'].append(analysis_method_json)

        return http_ok(project_json)

    def get_sample(self, project_id: int, sample_index: int) -> flask.Response:
        """Retrieves the dataset sample with the specified index from the specified project.

        Args:
            project_id (int): The ID of the project from which the dataset sample is to be retrieved.
            sample_index (int): The index of the dataset sample that is to be retrieved.

        Returns:
            flask.Response: Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the dataset sample. If the
                specified project does not exist, then an HTTP 404 Not Found response is returned. If the specified dataset sample does not exist,
                then an HTTP 404 Not Found response is returned.
        """

        # Checks if a project with the specified ID exists
        if project_id >= len(self.workspace.projects):
            return http_not_found(f'The project with the ID {project_id} could not be found.', self.is_in_debug_mode)
        project = self.workspace.get_project(self.workspace.get_project_names()[project_id])

        # Retrieves the dataset sample with the specified index
        try:
            sample = project.get_sample(sample_index)
        except LookupError as error:
            return http_not_found(error, self.is_in_debug_mode)

        # Returns the retrieved dataset sample
        sample_json: SampleJson = {
            'index': sample.index,
            'labels': [],
            'width': sample.data.shape[0],
            'height': sample.data.shape[1],
            'url': flask.url_for('get_sample_image', project_id=project_id, sample_index=sample_index)
        }
        for label in sample.labels:
            sample_json['labels'].append({
                'index': label.index,
                'wordNetId': label.word_net_id,
                'name': label.name
            })
        return http_ok(sample_json)

    def get_sample_image(self, project_id: int, sample_index: int) -> flask.Response:
        """Retrieves the image of the dataset with the specified index from the specified project.

        Args:
            project_id (int): The ID of the project from which the dataset sample is to be retrieved.
            sample_index (int): The index of the dataset sample for which the image is to be retrieved.

        Returns:
            flask.Response: Returns an HTTP 200 OK response with the image of the specified dataset sample as content. If the specified project does
                not exist, then an HTTP 404 Not Found response is returned. If the specified dataset sample does not exist, then an HTTP 404 Not Found
                response is returned.
        """

        # Checks if a project with the specified ID exists
        if project_id >= len(self.workspace.projects):
            return http_not_found(f'The project with the ID {project_id} could not be found.', self.is_in_debug_mode)
        project = self.workspace.get_project(self.workspace.get_project_names()[project_id])

        # Retrieves the dataset sample with the specified index
        try:
            sample = project.get_sample(sample_index)
        except LookupError as error:
            return http_not_found(error, self.is_in_debug_mode)

        # Converts the NumPy array with the image data to a PIL image, encodes it as JPEG and returns it
        return send_image_file(sample.data)

    def get_attribution(self, project_id: int, attribution_index: int) -> flask.Response:
        """Retrieves the attribution with the specified index from the specified project.

        Args:
            project_id (int): The ID of the project from which the attribution is to be retrieved.
            attribution_index (int): The index of the attribution that is to be retrieved.

        Returns:
            flask.Response: Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the attribution. If the
                specified project does not exist, then an HTTP 404 Not Found response is returned. If the specified attribution does not exist, then
                an HTTP 404 Not Found response is returned.
        """

        # Checks if a project with the specified ID exists
        if project_id >= len(self.workspace.projects):
            return http_not_found(f'The project with the ID {project_id} could not be found.', self.is_in_debug_mode)
        project = self.workspace.get_project(self.workspace.get_project_names()[project_id])

        # Retrieves the attribution with the specified index
        try:
            attribution = project.get_attribution(attribution_index)
        except LookupError as error:
            return http_not_found(error, self.is_in_debug_mode)

        # Generates the JSON object that is to be returned to the client
        attribution_json: AttributionJson = {
            'index': attribution.index,
            'labels': [],
            'prediction': numpy.array(attribution.prediction).tolist(),
            'width': attribution.data.shape[0],
            'height': attribution.data.shape[1],
            'urls': {}
        }
        for label in attribution.labels:
            attribution_json['labels'].append({
                'index': label.index,
                'wordNetId': label.word_net_id,
                'name': label.name
            })
        image_mode = flask.request.args.get('imageMode', 'input')
        for color_map in self.color_maps:
            if image_mode in ('overlay', 'attribution'):
                url = flask.url_for(
                    'get_attribution_heatmap',
                    project_id=project_id,
                    attribution_index=attribution_index
                )
                superimpose = image_mode == 'overlay'
                attribution_json['urls'][color_map] = f'{url}?colorMap={color_map}&superimpose={superimpose}'
            else:
                attribution_json['urls'][color_map] = flask.url_for(
                    'get_sample_image',
                    project_id=project_id,
                    sample_index=attribution_index
                )

        # Returns the retrieved attribution
        return http_ok(attribution_json)

    def get_attribution_heatmap(self, project_id: int, attribution_index: int) -> flask.Response:
        """Renders a heatmap from the attribution with the specified index from the specified project.

        Args:
            project_id (int): The ID of the project from which the attribution is to be retrieved.
            attribution_index (int): The index of the attribution for which the heatmap is to be rendered.

        Returns:
            flask.Response: Returns an HTTP 200 OK response with the rendered heatmap image. If the specified project does not exist, then an HTTP 404
                Not Found response is returned. If the specified attribution does not exist, then an HTTP 404 Not Found response is returned.
        """

        # Checks if a project with the specified ID exists
        if project_id >= len(self.workspace.projects):
            return http_not_found(f'The project with the ID {project_id} could not be found.', self.is_in_debug_mode)
        project = self.workspace.get_project(self.workspace.get_project_names()[project_id])

        # Retrieves the attribution with the specified index
        try:
            attribution = project.get_attribution(attribution_index)
        except LookupError as error:
            return http_not_found(error, self.is_in_debug_mode)

        # Gets the color map that is to be used to convert the raw attribution to a heatmap from the URL parameters, if none was specified, then it
        # defaults to Black Fire-Red
        color_map_name = flask.request.args.get('colorMap', 'black-fire-red')

        # Renders the heatmap and returns it
        superimpose = flask.request.args.get('superimpose', 'false').upper() == 'TRUE'
        if superimpose:
            sample = project.get_sample(attribution.index)
            heatmap = attribution.render_heatmap(color_map_name, image_to_superimpose=sample.data)
        else:
            heatmap = attribution.render_heatmap(color_map_name)
        return send_image_file(heatmap)

    def get_analysis(self, project_id: int, analysis_method_name: str) -> flask.Response:
        """Retrieves the analysis from the specified project with the specified analysis method. Besides the project ID and the analysis method name,
        the name of the category, clustering, and embedding have to be specified as URL parameters.

        Args:
            project_id (int): The ID of the project from which the analysis is to be retrieved.
            analysis_method_name (str): The name of the analysis method from which the analysis is to be retrieved.

        Returns:
            flask.Response: Returns an HTTP 200 OK response with a JSON string as content, which contains the data of the analysis. If the specified
                project does not exist, then an HTTP 404 Not Found response is returned. If the specified analysis method does not exist, then an HTTP
                404 Not Found response is returned. If the analysis does not exist, then an HTTP 404 Not Found response is returned. If no category
                name, clustering name, or embedding name were specified in the URL parameters, then an HTTP 400 Bad Request response is returned.
        """

        # Checks if a project with the specified ID exists
        if project_id >= len(self.workspace.projects):
            return http_not_found(f'The project with the ID {project_id} could not be found.', self.is_in_debug_mode)
        project = self.workspace.get_project(self.workspace.get_project_names()[project_id])

        # Checks if the specified analysis method exists
        analysis_method_name = analysis_method_name.replace('-', '_')
        if analysis_method_name not in project.get_analysis_methods():
            return http_not_found(
                f'The specified analysis method "{analysis_method_name.replace("_", "-")}" could not be found.',
                self.is_in_debug_mode
            )

        # Retrieves the other parameters from the URL, if one is missing, an HTTP Bad Request response is returned
        category_name = flask.request.args.get('category')
        clustering_name = flask.request.args.get('clustering')
        embedding_name = flask.request.args.get('embedding')
        if category_name is None or clustering_name is None or embedding_name is None:
            return http_bad_request('No category, clustering, or embedding was specified.', self.is_in_debug_mode)

        # Gets the specified analysis
        try:
            analysis = project.get_analysis(analysis_method_name, category_name, clustering_name, embedding_name)
        except LookupError as error:
            return http_not_found(error, self.is_in_debug_mode)

        # The analysis consists mainly of three lists: one that contains the embedding array, one that contains the index of the attribution to which
        # the analysis belongs, and one that contains the cluster of the embeddings, this may be convenient in Python, but it is not in JavaScript, so
        # these three lists are combined into a single list containing the embeddings as objects
        clustering = numpy.array(analysis.clustering).tolist()
        embedding = numpy.array(analysis.embedding).tolist()
        attribution_indices = numpy.array(analysis.attribution_indices).tolist()
        zipped_embedding = []
        for index, sample_embedding in enumerate(embedding):
            zipped_embedding.append({
                'cluster': clustering[index],
                'attributionIndex': attribution_indices[index],
                'value': sample_embedding
            })

        # Creates the JSON object that is returned to the client
        analysis_json: AnalysisJson = {
            'categoryName': analysis.category_name,
            'humanReadableCategoryName': analysis.human_readable_category_name,
            'clusteringName': analysis.clustering_name,
            'embeddingName': analysis.embedding_name,
            'embedding': zipped_embedding
        }
        if analysis.eigenvalues is not None:
            analysis_json['eigenvalues'] = numpy.array(analysis.eigenvalues).tolist()

        # Returns the retrieved analysis
        return http_ok(analysis_json)

    def get_color_maps(self) -> flask.Response:
        """Retrieves the names of all the color maps that are supported.

        Returns:
            flask.Response: Returns an HTTP 200 OK response with a list of all the supported color maps as content.
        """

        color_maps = []
        for color_map_name, human_readable_name in self.color_maps.items():
            color_maps.append({
                'name': color_map_name,
                'humanReadableName': human_readable_name,
                'url': flask.url_for('get_color_map_preview', color_map=color_map_name)
            })
        return http_ok(color_maps)

    def get_color_map_preview(self, color_map: str) -> flask.Response:
        """Renders a preview of a color map with a value gradient. Using the URL parameters "width" and "height", the size of the preview can be
        specified. The size defaults to 200x20.

        Args:
            color_map (str): The name of the color map for which the preview is to be rendered.

        Returns:
            flask.Response: Returns an HTTP 200 OK response with the rendered heatmap preview. If the specified color map is unknown, then an HTTP 400
                Bad Request response is returned.
        """

        if color_map not in self.color_maps:
            return http_bad_request(f'The color map "{color_map}" is not supported.', self.is_in_debug_mode)

        width = int(flask.request.args.get('width', 200))
        height = int(flask.request.args.get('height', 20))

        heatmap = numpy.linspace(-1.0, 1.0, num=width)
        heatmap = numpy.repeat([heatmap], height, axis=0)
        heatmap = render_heatmap(heatmap, color_map)

        return send_image_file(heatmap)


class ProjectJson(TypedDict):
    """Represents a project in the JSON response of the RESTful API."""

    id: int
    """The ID of the project."""

    name: str
    """The name of the project."""

    model: str
    """The name of the model that is used in the project."""

    dataset: str
    """The name of the dataset that is used in the project."""

    analysisMethods: NotRequired[list['AnalysisMethodJson']]
    """The optional analysis methods that are available for the project."""


class AnalysisJson(TypedDict):
    """Represents an analysis in the JSON response of the RESTful API."""

    categoryName: str
    """The name of the category."""

    humanReadableCategoryName: str
    """The human-readable name of the category."""

    clusteringName: str
    """The name of the clustering."""

    embeddingName: str
    """The name of the embedding."""

    embedding: list[dict[str, Any]]
    """The embeddings of the analysis, where each embedding is represented as a dictionary that contains the cluster of the embedding, the index of
    the attribution to which the embedding belongs, and the value of the embedding.
    """

    eigenvalues: NotRequired[list[float]]
    """The optional eigenvalues of the analysis, if available."""


class AnalysisMethodJson(TypedDict):
    """Represents an analysis method in the JSON response of the RESTful API."""

    name: str
    """The name of the analysis method."""

    clusterings: list[str]
    """The names of the clusterings that are available for the analysis method."""

    categories: list['CategoryJson']
    """The categories that are available for the analysis method."""

    embeddings: list[str]
    """The names of the embeddings that are available for the analysis method."""


class CategoryJson(TypedDict):
    """Represents a category in the JSON response of the RESTful API."""

    name: str
    """The name of the category."""

    humanReadableName: str
    """The human-readable name of the category."""


class LabelJson(TypedDict):
    """Represents a label in the JSON response of the RESTful API."""

    index: int
    """The index of the label."""

    wordNetId: str
    """The WordNet ID of the label."""

    name: str
    """The name of the label."""


class SampleJson(TypedDict):
    """Represents a sample in the JSON response of the RESTful API."""

    index: int
    """The index of the sample."""

    labels: list[LabelJson]
    """The labels of the sample."""

    width: int
    """The width of the sample."""

    height: int
    """The height of the sample."""

    url: str
    """The URL of the image of the sample."""


class AttributionJson(TypedDict):
    """Represents an attribution in the JSON response of the RESTful API."""

    index: int
    """The index of the attribution."""

    labels: list[LabelJson]
    """The labels of the attribution."""

    prediction: list[float]
    """The prediction of the attribution."""

    width: int
    """The width of the attribution."""

    height: int
    """The height of the attribution."""

    urls: dict[str, str]
    """The URLs of the heatmaps of the attribution, where the key is the name of the color map and the value is the URL to the heatmap rendered in
    that color map.
    """


def http_ok(content: Any) -> flask.Response:
    """Generates an HTTP 200 OK response.

    Args:
        content (Any): The content that is to be converted into JSON and returned in the body of the response.

    Returns:
        flask.Response: Returns an HTTP 200 OK response.
    """

    response = flask.jsonify(content)
    response.status_code = 200
    return response


def http_bad_request(error: str | BaseException, add_debug_information: bool) -> flask.Response:
    """Generates an HTTP 400 Bad request response.

    Args:
        error (str | BaseException): The error that is to be returned in the body of the response.
        add_debug_information (bool): Determines whether debug information is added to the error message.

    Returns:
        flask.Response: Returns an HTTP 400 Bad Request response.
    """

    if isinstance(error, BaseException):
        error = format_exception(error, add_debug_information)

    response = flask.jsonify({'errorMessage': str(error)})
    response.status_code = 400
    return response


def http_not_found(error: str | BaseException, add_debug_information: bool) -> flask.Response:
    """Generates an HTTP 404 Not Found response.

    Args:
        error (str | BaseException): The error that is to be returned in the body of the response.
        add_debug_information (bool): Determines whether debug information is added to the error message.

    Returns:
        flask.Response: Returns an HTTP 404 Not found response.
    """

    if isinstance(error, BaseException):
        error = format_exception(error, add_debug_information)

    response = flask.jsonify({'errorMessage': str(error)})
    response.status_code = 404
    return response


def send_image_file(image: NDArray[numpy.float64] | Image.Image) -> flask.Response:
    """Converts the image to a JPEG image and generates a response which sends the image to the client.

    Args:
        image (NDArray[numpy.float64] | Image.Image): The image as a NumPy array that is to be send to the client.

    Returns:
        flask.Response: Returns a response, which contains the specified image as a JPEG encoded image file.
    """

    if isinstance(image, numpy.ndarray):
        image = Image.fromarray(image)
    in_memory_image_file = io.BytesIO()
    image.save(in_memory_image_file, format='JPEG', quality=70)
    in_memory_image_file.seek(0)
    return flask.send_file(in_memory_image_file, mimetype='image/jpeg')


def format_exception(exception: BaseException, add_debug_information: bool) -> str:
    """Formats the specified exception as a string so that it can be logged.

    Args:
        exception (BaseException): The exception that is to be formatted.
        add_debug_information (bool): Determines whether debug information is added to the string representation of the exception.

    Returns:
        str: Returns a string, which contains the error message of the exception. If the server is being run in debug mode, then the traceback is also
            included in the string that is returned.
    """

    error_message = str(exception)
    if add_debug_information:
        error_message = '{0}\n{1}'.format(
            error_message,
            '\n'.join(traceback.format_tb(exception.__traceback__))
        )
    return error_message
