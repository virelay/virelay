#!/usr/bin/env python3

"""The installation script for ViRelAy."""

from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as read_me_file:
    long_description = read_me_file.read()

setup(
    name='virelay',
    use_scm_version=True,
    author='chrstphr',
    author_email='virelay@j0d.de',
    description='Web-app to view source-data, attributions, clusterings, and (t-SNE-)embeddings.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/virelay/virelay',
    packages=find_packages(include=['virelay*']),
    install_requires=[
        'flask-cors>=5.0.0,<6.0.0',
        'flask>=3.0.3,<4.0.0',
        'gunicorn>=23.0.0,<24.0.0',
        'h5py>=3.12.1,<4.0.0',
        'matplotlib>=3.9.2,<4.0.0',
        'numpy>=2.1.1,<3.0.0',
        'pillow>=10.4.0,<11.0.0',
        'pyyaml>=6.0.2,<7.0.0'
    ],
    setup_requires=[
        'setuptools_scm>=8.1.0,<9.0.0'
    ],
    extras_require={
        'docs': [
            'sphinx-copybutton>=0.5.2,<1.0.0',
            'sphinx-rtd-theme>=2.0.0,<3.0.0',
            'sphinxcontrib.bibtex>=2.6.3,<3.0.0',
            'sphinxcontrib.datatemplates>=0.11.0,<1.0.0'
        ],
        'tests': [
            'coverage>=7.6.1,<8.0.0',
            'pytest-cov>=5.0.0,<6.0.0',
            'pytest>=8.3.3,<9.0.0'
        ],
        'linting': [
            'mypy>=1.11.2,<2.0.0',
            'pycodestyle>=2.12.1,<3.0.0',
            'pydoclint>=0.5.8,<1.0.0',
            'pylint>=3.3.1,<4.0.0',
            'types-Flask-Cors>=5.0.0.20240902,<6.0.0',
            'types-PyYAML>=6.0.12.20240917,<7.0.0',
            'types-setuptools>=75.1.0.20240917,<76.0.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'virelay = virelay.__main__:main'
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
    },
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ]
)
