"""Vispr command-line interface to run the Bokeh server."""

import logging
from sys import stderr

import click
from bokeh.server.server import Server

from .server_application import modify_doc

@click.command()
@click.argument('input_path', type=click.Path())
@click.argument('attribution_path', type=click.Path())
@click.argument('analysis_path', type=click.Path())
@click.argument('wordmap', type=click.Path())
@click.argument('wnids', type=click.Path())
@click.option('--port', type=int, default=5096)
@click.option('--address', default='127.0.0.1')
@click.option('--allow-websocket-origin', multiple=True, default=['127.0.0.1:5096'])
@click.option('--num-procs', type=int, default=1)
@click.option('--log', type=click.File(), default=stderr)
@click.option('-v', '--verbose', count=True)
def main(
        input_path,
        attribution_path,
        analysis_path,
        wordmap,
        wnids,
        port,
        address,
        allow_websocket_origin,
        num_procs,
        log,
        verbose
    ):
    """
    Starts the Vispr Bokeh server.

    Parameters:
    -----------
        input_path: str
            The path to the directory that contains the images of the dataset.
        attribution_path: str
            The path to the HDF5 file that contains the attributions.
        analysis_path: str
            The path to the HDF5 file that contains the analysis.
        wordmap: str
            The path to the JSON file that contains the mappings between the WordNet IDs and human-readable class names.
        wnids: str
            The path to the text file that contains the WordNet IDs of the classes of the classifier.
        port: int
            The number of the port on which the server should run. Defaults to 5096.
        address: str
            The IP address at which the server should run. Defaults to 127.0.0.1.
        allow_websocket_origin: list
            The origins from which requests are allowed. Defaults to 127.0.0.1:5096.
        num_procs: int
            The number of processes that the server is allowed to use. Defaults to 1.
        log: io.TextIOBase
            The file to which the logs are written to. Defaults to stderr.
        verbose: int
            The verbosity level of the logging.
    """

    # Initializes the logging
    logger = logging.getLogger(__name__)
    root_logger = logging.getLogger()
    log_handler = logging.StreamHandler(log)
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(log_handler)
    root_logger.setLevel(logging.DEBUG if verbose > 0 else logging.INFO)

    # Starts the Bokeh server
    logger.info('Starting server at %s', '{0}:{1}'.format(address, port))
    server_kwargs = {
        'port': port,
        'address': address,
        'allow_websocket_origin': list(allow_websocket_origin),
        'num_procs': num_procs,
    }
    server = Server({
        '/': (lambda doc: modify_doc(doc, input_path, attribution_path, analysis_path, wordmap, wnids))
    }, **server_kwargs)
    server.io_loop.add_callback(server.show, '/')
    server.run_until_shutdown()
