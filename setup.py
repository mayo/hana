#!/usr/bin/env python

from setuptools import setup
from codecs import open
from os import path

basedir = path.abspath(path.dirname(__file__))

with open(path.join(basedir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='hana',
    version='0.0.1',

    description='Static site generator',
    long_description=long_description,

    author='Mayo Jordanov',
    author_email='mayo@oyam.ca',

    url='https://github.com/mayo/hana',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'License :: Other/Proprietary License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    keywords='hana static site generator processing file',

    packages=['hana'],

#    entry_points={
#        'console_scripts': [
#            'hana = hana.core:main',
#        ]
#    }
)

