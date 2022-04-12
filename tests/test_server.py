"""Contains the tests for the REST server of ViRelAy."""
# pylint: disable=too-many-lines

import os
import io
import re
import glob

import numpy
from PIL import Image
from flask import Flask, Response
from flask.testing import FlaskClient

from virelay.server import http_ok, http_bad_request, http_not_found, send_image_file, format_exception

NUMBER_OF_CLASSES = 3
NUMBER_OF_SAMPLES = 40


class TestServer:
    """Represents the tests for the Server class."""

    @staticmethod
    def test_angular_frontend_is_not_served_in_debug_mode(test_client_with_app_in_debug_model: FlaskClient):
        """Tests whether the ViRelAy server does not serve the Angular frontend files when started in debug mode

        Parameters
        ----------
            test_client_with_app_in_debug_model: FlaskClient
                The HTTP client that is used for the tests.
        """

        http_response = test_client_with_app_in_debug_model.get('/')
        assert http_response.status_code == 404

        http_response = test_client_with_app_in_debug_model.get('/index.html')
        assert http_response.status_code == 404

        http_response = test_client_with_app_in_debug_model.get('/favicon.ico')
        assert http_response.status_code == 404

        http_response = test_client_with_app_in_debug_model.get('/styles.css')
        assert http_response.status_code == 404

        http_response = test_client_with_app_in_debug_model.get('/main.js')
        assert http_response.status_code == 404

        http_response = test_client_with_app_in_debug_model.get('/assets/images/virelay-logo.png')
        assert http_response.status_code == 404

    @staticmethod
    def test_angular_frontend_is_served_when_server_is_not_in_debug_mode(test_client: FlaskClient):
        """Tests whether the ViRelAy server serves the Angular frontend files when not started in debug mode

        Parameters
        ----------
            test_client: FlaskClient
                The HTTP client that is used for the tests.
        """

        http_response = test_client.get('/')
        assert http_response.status_code == 200
        assert http_response.content_type == 'text/html; charset=utf-8'

        http_response = test_client.get('/index.html')
        assert http_response.status_code == 200
        assert http_response.content_type == 'text/html; charset=utf-8'

        http_response = test_client.get('/favicon.ico')
        assert http_response.status_code == 200
        assert http_response.content_type == 'image/vnd.microsoft.icon'

        styles_file_name = os.path.basename(glob.glob(os.path.join(
            os.getcwd(),
            'virelay',
            'frontend',
            'distribution',
            'styles.*.css'
        ))[0])
        http_response = test_client.get(f'/{styles_file_name}')
        assert http_response.status_code == 200
        assert http_response.content_type == 'text/css; charset=utf-8'

        main_file_name = os.path.basename(glob.glob(os.path.join(
            os.getcwd(),
            'virelay',
            'frontend',
            'distribution',
            'main.*.js'
        ))[0])
        http_response = test_client.get(f'/{main_file_name}')
        assert http_response.status_code == 200
        assert http_response.content_type == 'application/javascript; charset=utf-8'

        http_response = test_client.get('/assets/images/virelay-logo.png')
        assert http_response.status_code == 200
        assert http_response.content_type == 'image/png'

    @staticmethod
    def test_get_projects(test_client: FlaskClient) -> None:
        """Tests whether the ViRelAy server correctly serves the projects in the workspace.

        Parameters
        ----------
            test_client_with_app_in_debug_model: FlaskClient
                The HTTP client that is used for the tests.
        """

        http_response = test_client.get('/api/projects')
        projects = http_response.get_json()
        assert http_response.status_code == 200
        assert http_response.content_type == 'application/json'
        assert len(projects) == 1
        assert projects[0]['id'] == 0
        assert projects[0]['name'] == 'Test Project'
        assert projects[0]['model'] == 'No Model'
        assert projects[0]['dataset'] == 'HDF5 Dataset'

    @staticmethod
    def test_get_project_by_id(test_client: FlaskClient) -> None:
        """Tests whether the ViRelAy server correctly serves a project by ID.

        Parameters
        ----------
            test_client_with_app_in_debug_model: FlaskClient
                The HTTP client that is used for the tests.
        """

        http_response = test_client.get('/api/projects/0')
        project = http_response.get_json()
        assert http_response.status_code == 200
        assert http_response.content_type == 'application/json'
        assert project['id'] == 0
        assert project['name'] == 'Test Project'
        assert project['model'] == 'No Model'
        assert project['dataset'] == 'HDF5 Dataset'
        assert len(project['analysisMethods']) == 1
        assert project['analysisMethods'][0]['name'] == "Spectral Analysis"
        assert project['analysisMethods'][0]['clusterings'][0] == 'agglomerative-02'
        assert project['analysisMethods'][0]['clusterings'][1] == 'agglomerative-03'
        assert project['analysisMethods'][0]['clusterings'][2] == 'dbscan-eps=0.2'
        assert project['analysisMethods'][0]['clusterings'][3] == 'dbscan-eps=0.3'
        assert project['analysisMethods'][0]['clusterings'][4] == 'hdbscan'
        assert project['analysisMethods'][0]['clusterings'][5] == 'kmeans-02'
        assert project['analysisMethods'][0]['clusterings'][6] == 'kmeans-03'
        assert project['analysisMethods'][0]['categories'] == [
            {'humanReadableName': 'Class 0', 'name': '00000000'},
            {'humanReadableName': 'Class 1', 'name': '00000001'},
            {'humanReadableName': 'Class 2', 'name': '00000002'}
        ]
        assert project['analysisMethods'][0]['embeddings'] == ['spectral', 'tsne', 'umap']

        http_response = test_client.get('/api/projects/1')
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'

    @staticmethod
    def test_get_sample(test_client: FlaskClient) -> None:
        """Tests whether the ViRelAy server correctly serves a sample.

        Parameters
        ----------
            test_client_with_app_in_debug_model: FlaskClient
                The HTTP client that is used for the tests.
        """

        http_response = test_client.get('/api/projects/0/dataset/0')
        sample = http_response.get_json()
        assert http_response.status_code == 200
        assert http_response.content_type == 'application/json'
        assert sample['index'] == 0
        assert sample['labels'] == ['Class 0']
        assert sample['width'] == 32
        assert sample['height'] == 32
        assert sample['url'] == '/api/projects/0/dataset/0/image'

        http_response = test_client.get('/api/projects/1/dataset/0')
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'

        http_response = test_client.get(f'/api/projects/0/dataset/{NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES}')
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'

    @staticmethod
    def test_get_sample_image(test_client: FlaskClient) -> None:
        """Tests whether the ViRelAy server correctly serves a sample image.

        Parameters
        ----------
            test_client_with_app_in_debug_model: FlaskClient
                The HTTP client that is used for the tests.
        """

        http_response = test_client.get('/api/projects/0/dataset/0/image')
        assert http_response.status_code == 200
        assert http_response.content_type == 'image/jpeg'
        actual_image_data = numpy.array(Image.open(io.BytesIO(http_response.get_data())))
        assert actual_image_data.shape == (32, 32, 3)

        http_response = test_client.get('/api/projects/1/dataset/0/image')
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'

        http_response = test_client.get(f'/api/projects/0/dataset/{NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES}/image')
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'

    @staticmethod
    def test_get_attribution(test_client: FlaskClient) -> None:
        """Tests whether the ViRelAy server correctly serves an attribution.

        Parameters
        ----------
            test_client_with_app_in_debug_model: FlaskClient
                The HTTP client that is used for the tests.
        """

        http_response = test_client.get('/api/projects/0/attributions/0')
        assert http_response.status_code == 200
        assert http_response.content_type == 'application/json'
        attribution = http_response.get_json()
        assert attribution['index'] == 0
        assert attribution['labels'] == ['Class 0']
        assert len(attribution['prediction']) == NUMBER_OF_CLASSES
        assert attribution['width'] == 32
        assert attribution['height'] == 32
        assert attribution['urls']['afm-hot'] == '/api/projects/0/dataset/0/image'
        assert attribution['urls']['black-fire-red'] == '/api/projects/0/dataset/0/image'
        assert attribution['urls']['black-green'] == '/api/projects/0/dataset/0/image'
        assert attribution['urls']['black-yellow'] == '/api/projects/0/dataset/0/image'
        assert attribution['urls']['blue-white-red'] == '/api/projects/0/dataset/0/image'
        assert attribution['urls']['gray-red'] == '/api/projects/0/dataset/0/image'
        assert attribution['urls']['jet'] == '/api/projects/0/dataset/0/image'
        assert attribution['urls']['seismic'] == '/api/projects/0/dataset/0/image'

        http_response = test_client.get('/api/projects/0/attributions/0?image_mode=attribution')
        assert http_response.status_code == 200
        assert http_response.content_type == 'application/json'
        attribution = http_response.get_json()
        assert attribution['index'] == 0
        assert attribution['labels'] == ['Class 0']
        assert len(attribution['prediction']) == NUMBER_OF_CLASSES
        assert attribution['width'] == 32
        assert attribution['height'] == 32
        assert attribution['urls']['afm-hot'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=afm-hot&superimpose=False'
        assert attribution['urls']['black-fire-red'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=black-fire-red&superimpose=False'
        assert attribution['urls']['black-green'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=black-green&superimpose=False'
        assert attribution['urls']['black-yellow'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=black-yellow&superimpose=False'
        assert attribution['urls']['blue-white-red'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=blue-white-red&superimpose=False'
        assert attribution['urls']['gray-red'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=gray-red&superimpose=False'
        assert attribution['urls']['jet'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=jet&superimpose=False'
        assert attribution['urls']['seismic'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=seismic&superimpose=False'

        http_response = test_client.get('/api/projects/0/attributions/0?image_mode=overlay')
        assert http_response.status_code == 200
        assert http_response.content_type == 'application/json'
        attribution = http_response.get_json()
        assert attribution['index'] == 0
        assert attribution['labels'] == ['Class 0']
        assert len(attribution['prediction']) == NUMBER_OF_CLASSES
        assert attribution['width'] == 32
        assert attribution['height'] == 32
        assert attribution['urls']['afm-hot'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=afm-hot&superimpose=True'
        assert attribution['urls']['black-fire-red'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=black-fire-red&superimpose=True'
        assert attribution['urls']['black-green'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=black-green&superimpose=True'
        assert attribution['urls']['black-yellow'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=black-yellow&superimpose=True'
        assert attribution['urls']['blue-white-red'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=blue-white-red&superimpose=True'
        assert attribution['urls']['gray-red'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=gray-red&superimpose=True'
        assert attribution['urls']['jet'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=jet&superimpose=True'
        assert attribution['urls']['seismic'] == \
            '/api/projects/0/attributions/0/heatmap?colorMap=seismic&superimpose=True'

        http_response = test_client.get('/api/projects/1/attributions/0')
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'

        http_response = test_client.get(f'/api/projects/0/attributions/{NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES}')
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'

    @staticmethod
    def test_get_attribution_heatmap(test_client: FlaskClient) -> None:
        """Tests whether the ViRelAy server correctly serves an attribution heatmap.

        Parameters
        ----------
            test_client_with_app_in_debug_model: FlaskClient
                The HTTP client that is used for the tests.
        """

        http_response = test_client.get('/api/projects/0/dataset/0/image')
        assert http_response.status_code == 200
        assert http_response.content_type == 'image/jpeg'
        actual_image_data = numpy.array(Image.open(io.BytesIO(http_response.get_data())))
        assert actual_image_data.shape == (32, 32, 3)

        http_response = test_client.get('/api/projects/0/attributions/0/heatmap?colorMap=afm-hot&superimpose=False')
        assert http_response.status_code == 200
        assert http_response.content_type == 'image/jpeg'
        actual_image_data = numpy.array(Image.open(io.BytesIO(http_response.get_data())))
        assert actual_image_data.shape == (32, 32, 3)

        http_response = test_client.get('/api/projects/0/attributions/0/heatmap?colorMap=afm-hot&superimpose=True')
        assert http_response.status_code == 200
        assert http_response.content_type == 'image/jpeg'
        actual_image_data = numpy.array(Image.open(io.BytesIO(http_response.get_data())))
        assert actual_image_data.shape == (32, 32, 3)

        http_response = test_client.get('/api/projects/1/attributions/0/heatmap')
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'

        http_response = test_client.get(f'/api/projects/0/attributions/{NUMBER_OF_CLASSES * NUMBER_OF_SAMPLES}/heatmap')
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'

    @staticmethod
    def test_get_analysis(test_client: FlaskClient) -> None:
        """Tests whether the ViRelAy server correctly serves an analysis.

        Parameters
        ----------
            test_client_with_app_in_debug_model: FlaskClient
                The HTTP client that is used for the tests.
        """

        http_response = test_client.get(
            '/api/projects/0/analyses/Spectral%20Analysis?category=00000000&clustering=hdbscan&embedding=spectral'
        )
        analysis = http_response.get_json()
        assert http_response.status_code == 200
        assert http_response.content_type == 'application/json'
        assert analysis['categoryName'] == '00000000'
        assert analysis['humanReadableCategoryName'] == 'Class 0'
        assert analysis['clusteringName'] == 'hdbscan'
        assert analysis['embeddingName'] == 'spectral'
        assert 'eigenvalues' in analysis
        assert len(analysis['embedding']) == NUMBER_OF_SAMPLES

        http_response = test_client.get('/api/projects/0/analyses/Spectral%20Analysis')
        assert http_response.status_code == 400
        assert http_response.content_type == 'application/json'

        http_response = test_client.get(
            '/api/projects/0/analyses/Spectral%20Analysis?category=00000003&clustering=hdbscan&embedding=spectral'
        )
        analysis = http_response.get_json()
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'

        http_response = test_client.get('/api/projects/1/analyses/unknown-analysis-method')
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'

        http_response = test_client.get('/api/projects/0/analyses/unknown-analysis-method')
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'

    @staticmethod
    def test_get_analysis_without_eigenvalues(test_client_without_eigenvalues_in_analysis: FlaskClient) -> None:
        """Tests whether the ViRelAy server correctly serves an analysis without eigenvalues for a project whose
        analysis database does not contain eigenvalues.

        Parameters
        ----------
            test_client_with_app_in_debug_model: FlaskClient
                The HTTP client that is used for the tests.
        """

        http_response = test_client_without_eigenvalues_in_analysis.get(
            '/api/projects/0/analyses/Spectral%20Analysis?category=00000000&clustering=hdbscan&embedding=spectral'
        )
        analysis = http_response.get_json()
        assert http_response.status_code == 200
        assert http_response.content_type == 'application/json'
        assert analysis['categoryName'] == '00000000'
        assert analysis['humanReadableCategoryName'] == 'Class 0'
        assert analysis['clusteringName'] == 'hdbscan'
        assert analysis['embeddingName'] == 'spectral'
        assert 'eigenvalues' not in analysis
        assert len(analysis['embedding']) == NUMBER_OF_SAMPLES

    @staticmethod
    def test_get_color_maps(test_client: FlaskClient) -> None:
        """Tests whether the ViRelAy server correctly serves color maps.

        Parameters
        ----------
            test_client_with_app_in_debug_model: FlaskClient
                The HTTP client that is used for the tests.
        """

        http_response = test_client.get('/api/color-maps')
        color_maps = http_response.get_json()
        assert http_response.status_code == 200
        assert http_response.content_type == 'application/json'
        assert color_maps[0]['humanReadableName'] == 'Gray Red'
        assert color_maps[0]['name'] == 'gray-red'
        assert color_maps[0]['url'] == '/api/color-maps/gray-red'
        assert color_maps[1]['humanReadableName'] == 'Black Green'
        assert color_maps[1]['name'] == 'black-green'
        assert color_maps[1]['url'] == '/api/color-maps/black-green'
        assert color_maps[2]['humanReadableName'] == 'Black Fire-Red'
        assert color_maps[2]['name'] == 'black-fire-red'
        assert color_maps[2]['url'] == '/api/color-maps/black-fire-red'
        assert color_maps[3]['humanReadableName'] == 'Black Yellow'
        assert color_maps[3]['name'] == 'black-yellow'
        assert color_maps[3]['url'] == '/api/color-maps/black-yellow'
        assert color_maps[4]['humanReadableName'] == 'Blue White Red'
        assert color_maps[4]['name'] == 'blue-white-red'
        assert color_maps[4]['url'] == '/api/color-maps/blue-white-red'
        assert color_maps[5]['humanReadableName'] == 'AFM Hot'
        assert color_maps[5]['name'] == 'afm-hot'
        assert color_maps[5]['url'] == '/api/color-maps/afm-hot'
        assert color_maps[6]['humanReadableName'] == 'Jet'
        assert color_maps[6]['name'] == 'jet'
        assert color_maps[6]['url'] == '/api/color-maps/jet'
        assert color_maps[7]['humanReadableName'] == 'Seismic'
        assert color_maps[7]['name'] == 'seismic'
        assert color_maps[7]['url'] == '/api/color-maps/seismic'

    @staticmethod
    def test_get_color_map_preview(test_client: FlaskClient) -> None:
        """Tests whether the ViRelAy server correctly serves color map previews.

        Parameters
        ----------
            test_client_with_app_in_debug_model: FlaskClient
                The HTTP client that is used for the tests.
        """

        color_maps = [
            'gray-red',
            'black-green',
            'black-fire-red',
            'black-yellow',
            'blue-white-red',
            'afm-hot',
            'jet',
            'seismic'
        ]
        for color_map in color_maps:
            http_response = test_client.get(f'/api/color-maps/{color_map}')
            assert http_response.status_code == 200
            assert http_response.content_type == 'image/jpeg'
            actual_image_data = numpy.array(Image.open(io.BytesIO(http_response.get_data())))
            assert actual_image_data.shape == (20, 200, 3)

            http_response = test_client.get(f'/api/color-maps/{color_map}?width=64&height=32')
            assert http_response.status_code == 200
            assert http_response.content_type == 'image/jpeg'
            actual_image_data = numpy.array(Image.open(io.BytesIO(http_response.get_data())))
            assert actual_image_data.shape == (32, 64, 3)

        http_response = test_client.get('/api/color-maps/unknown-color-map')
        assert http_response.status_code == 400
        assert http_response.content_type == 'application/json'


def test_http_ok(app_with_empty_workspace: Flask) -> None:
    """Tests the function for creating an HTTP 200 OK response.

    Parameters
    ----------
        app_with_empty_workspace: Flask
            The Flask application that is used for the test.
    """

    with app_with_empty_workspace.app_context():

        http_response: Response = http_ok({'result': 'This is a result.'})
        assert http_response.content_type == 'application/json'
        assert http_response.status_code == 200
        assert http_response.content_type == 'application/json'
        assert http_response.get_json()['result'] == 'This is a result.'


def test_http_bad_request(app_with_empty_workspace: Flask) -> None:
    """Tests the function for creating an HTTP 400 Bad Request response.

    Parameters
    ----------
        app_with_empty_workspace: Flask
            The Flask application that is used for the test.
    """

    with app_with_empty_workspace.app_context():
        try:
            raise ValueError('This is an error message.')
        except ValueError as exception:
            http_response: Response = http_bad_request(exception, False)
            assert http_response.status_code == 400
            assert http_response.content_type == 'application/json'
            assert http_response.get_json()['errorMessage'] == 'This is an error message.'

            http_response: Response = http_bad_request(exception, True)
            assert http_response.status_code == 400
            assert http_response.content_type == 'application/json'
            assert re.match(
                r'This is an error message.\n'
                r'  File ".*/test_server.py"\, line [0-9]+\, in test_http_bad_request\n'
                r'    raise ValueError\(\'This is an error message\.\'\)',
                http_response.get_json()['errorMessage']
            )

        http_response: Response = http_bad_request('This is an error message.', False)
        assert http_response.content_type == 'application/json'
        assert http_response.status_code == 400
        assert http_response.get_json()['errorMessage'] == 'This is an error message.'


def test_http_not_found(app_with_empty_workspace: Flask) -> None:
    """Tests the function for creating an HTTP 404 Not Found response.

    Parameters
    ----------
        app_with_empty_workspace: Flask
            The Flask application that is used for the test.
    """

    with app_with_empty_workspace.app_context():
        try:
            raise ValueError('This is an error message.')
        except ValueError as exception:
            http_response: Response = http_not_found(exception, False)
            assert http_response.status_code == 404
            assert http_response.content_type == 'application/json'
            assert http_response.get_json()['errorMessage'] == 'This is an error message.'

            http_response: Response = http_not_found(exception, True)
            assert http_response.status_code == 404
            assert http_response.content_type == 'application/json'
            assert re.match(
                r'This is an error message.\n'
                r'  File ".*/test_server.py"\, line [0-9]+\, in test_http_not_found\n'
                r'    raise ValueError\(\'This is an error message\.\'\)',
                http_response.get_json()['errorMessage']
            )

        http_response: Response = http_not_found('This is an error message.', False)
        assert http_response.status_code == 404
        assert http_response.content_type == 'application/json'
        assert http_response.get_json()['errorMessage'] == 'This is an error message.'


def test_send_image_file(app_with_empty_workspace: Flask) -> None:
    """Tests the function for sending an image file to the client.

    Parameters
    ----------
        app_with_empty_workspace: Flask
            The Flask application that is used for the test.
    """

    with app_with_empty_workspace.test_request_context():
        image = Image.new('RGB', (32, 32), color=(255, 255, 255))
        expected_image_data = numpy.array(image)

        http_response: Response = send_image_file(image)
        http_response.direct_passthrough = False
        actual_image_data = numpy.array(Image.open(io.BytesIO(http_response.get_data())))
        assert http_response.status_code == 200
        assert http_response.content_type == 'image/jpeg'
        assert numpy.array_equal(expected_image_data, actual_image_data)

        http_response: Response = send_image_file(numpy.array(image))
        http_response.direct_passthrough = False
        actual_image_data = numpy.array(Image.open(io.BytesIO(http_response.get_data())))
        assert http_response.status_code == 200
        assert http_response.content_type == 'image/jpeg'
        assert numpy.array_equal(expected_image_data, actual_image_data)


def test_format_exception() -> None:
    """Tests the function for formatting exception messages."""

    try:
        raise ValueError('This is an error message.')
    except ValueError as exception:
        error_message = format_exception(exception, False)
        assert error_message == 'This is an error message.'

        error_message = format_exception(exception, True)
        assert re.match(
            r'This is an error message.\n'
            r'  File ".*/test_server.py"\, line [0-9]+\, in test_format_exception\n'
            r'    raise ValueError\(\'This is an error message\.\'\)',
            error_message
        )
