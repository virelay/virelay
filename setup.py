#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="vispr",
    version="0.1",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        'h5py>=2.10.0',
        'matplotlib>=3.2.2',
        'numpy>=1.19.0',
        'Pillow>=7.2.0',
        'flask>=1.1.2',
        'flask_cors>=3.0.8',
        'pyyaml>=5.3.1'
    ],
    entry_points={
        'console_scripts': [
            'vispr = vispr.__main__:main',
        ]
    },
    package_data={
        'vispr': [
            'frontend/distribution/index.html',
            'frontend/distribution/favicon.ico',
            'frontend/distribution/*.js',
            'frontend/distribution/*.css',
            'frontend/distribution/assets/images/*.png',
            'frontend/distribution/3rdpartylicenses.txt'
        ]
    }
)
