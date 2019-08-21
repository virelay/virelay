"""Contains the entry-point to the VISPR application."""

from .application import Application


if __name__ == '__main__':
    APPLICATION = Application()
    APPLICATION.run()
