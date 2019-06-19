#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name = "sprincl",
    version = "0.1",
    packages=find_packages(),
    install_requires=[
        'h5py>=2.9.0',
        'matplotlib>=3.0.3',
        'numpy>=1.16.3',
        'scikit-learn>=0.20.3',
        'scipy>=1.2.1',
        'Click>=7.0',
    ],
)
