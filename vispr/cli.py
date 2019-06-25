import logging
from sys import stdout

import click
from bokeh.server.server import Server

from .handler import modify_doc

logger = logging.getLogger(__name__)

@click.command()
@click.argument('input_path', type=click.Path())
@click.argument('attribution_path', type=click.Path())
@click.argument('analysis_path', type=click.Path())
@click.argument('wordmap', type=click.Path())
@click.option('--port', type=int, default=5096)
@click.option('--address', default='127.0.0.1')
@click.option('--allow-websocket-origin', multiple=True, default=['127.0.0.1:5096'])
@click.option('--num-procs', type=int, default=1)
@click.option('--log', type=click.File(), default=stdout)
@click.option('-v', '--verbose', count=True)
def main(input_path, attribution_path, analysis_path, wordmap, port, address, allow_websocket_origin, num_procs, log,
         verbose):
    logger.addHandler(logging.StreamHandler(log))
    logger.setLevel(logging.DEBUG if verbose > 0 else logging.INFO)

    server_kwargs = {
        'port': port,
        'address': address,
        'allow_websocket_origin': list(allow_websocket_origin),
        'num_procs': num_procs,
    }

    server = Server({'/': (lambda doc: modify_doc(doc, input_path, attribution_path, analysis_path, wordmap))},
                    **server_kwargs)

    server.io_loop.add_callback(server.show, '/')
    server.run_until_shutdown()

