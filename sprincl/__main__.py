"""SPRINCL module invocation.

"""
from .cli import main as cli_main


def main():
    """Execute SPRINCL command line interface.

    """
    # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
    cli_main(auto_envvar_prefix='SPRINCL')


if __name__ == '__main__':
    main()
