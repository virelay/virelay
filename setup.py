#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='virelay',
    use_scm_version=True,
    packages=['virelay'],
    install_requires=[
        'h5py>=2.10.0',
        'matplotlib>=3.2.2',
        'numpy>=1.19.0',
        'Pillow>=7.2.0',
        'flask>=1.1.2',
        'flask_cors>=3.0.8',
        'pyyaml>=5.3.1',
        'gunicorn>=20.0.4'
    ],
    setup_requires=[
        'setuptools_scm',
    ],
    entry_points={
        'console_scripts': [
            'virelay = virelay.__main__:main',
        ]
    },
    package_data={
        'virelay': [
            'frontend/distribution/index.html',
            'frontend/distribution/favicon.ico',
            'frontend/distribution/*.js',
            'frontend/distribution/*.css',
            'frontend/distribution/assets/images/*.png',
            'frontend/distribution/3rdpartylicenses.txt'
        ]
    }
)
