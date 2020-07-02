#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="vispr",
    version="0.1",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        'h5py>=2.9.0',
        'matplotlib>=3.0.3',
        'numpy>=1.16.3',
        'Click>=7.0',
        'Pillow',
        'flask',
        'flask_cors'
    ],
    entry_points={
        'console_scripts': [
            'vispr = vispr.cli:main',
        ]
    },
)
