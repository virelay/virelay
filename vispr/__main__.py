"""__main__ module invocation of vispr

"""
from .cli import main as cli_main


def main():
    """Execute vispr command-line interface

    """
    # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
    cli_main(auto_envvar_prefix='VISPR')


if __name__ == '__main__':
    main()
