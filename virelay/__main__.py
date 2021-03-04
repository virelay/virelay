"""Contains the entry-point to the ViRelAy application."""

from .application import Application

def main():
    APPLICATION = Application()
    APPLICATION.run()

if __name__ == '__main__':
    main()
