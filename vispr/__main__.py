from .cli import main as cli_main


def main():
    # pylint: disable=no-value-for-parameter
    cli_main(auto_envvar_prefix='VISPR')


if __name__ == '__main__':
    main()
