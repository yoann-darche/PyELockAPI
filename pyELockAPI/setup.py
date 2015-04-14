# -*- coding: utf-8 -*-

__author__ = 'daryo01'

from setuptools import setup, find_packages

import pyELockAPI

setup(

    # Lib Name
    name='pyELockAPI',

    # Version
    version=pyELockAPI.__version__,

    # Dependant package list
    packages=find_packages(),

    author='Yoann Darche',
    author_email='y oann d AT hot mail dot com',

    description='Basic API for ELock Elektor''s card',
    long_description=open('README.md').read(),

    url='https://github.com/yoann-darche/pyELockAPI.git',

    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Topic :: System :: Hardware :: Hardware Drivers",

    ],

    license="WTFPL"

)