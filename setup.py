#!/usr/bin/env python3
from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as fd:
    long_description = fd.read()


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
    },
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
