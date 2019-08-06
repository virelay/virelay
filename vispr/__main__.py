"""The entry-point to the Vispr command line application."""

from .cli import main as cli_main

def main():
    """Executes the Vispr command-line interface."""

    # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
    cli_main(auto_envvar_prefix='VISPR')

# If the module is executed, the main function is invoked
if __name__ == '__main__':
    main()
