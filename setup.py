#!/usr/bin/env python

from setuptools import setup
from codecs import open
from os import path

basedir = path.abspath(path.dirname(__file__))

with open(path.join(basedir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='hana',
    version='0.0.dev5',

    description='Static site generator',
    long_description=long_description,

    install_requires=[
        'pathspec>=0.5.2',
    ],

    author='Mayo Jordanov',
    author_email='mayo@oyam.ca',

    url='https://github.com/mayo/hana',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Environment :: Console',

        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',

        'License :: OSI Approved :: MIT License',

        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: Unix',

        'Programming Language :: Python',

        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Code Generators',
    ],

    keywords='hana static site generator processing file',

    packages=[
        'hana',
        'hana.plugins'
    ],

    entry_points={
#        'console_scripts': [
#            'hana = hana.core:main',
#        ],
        'hana.plugins': [
            'file_loader = hana.plugins.file_loader.FileLoader',
            'file_writer = hana.plugins.file_writer.FileWriter',
        ]
    }
)

