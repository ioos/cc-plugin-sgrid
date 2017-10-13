#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


def version():
    with open('VERSION') as f:
        return f.read().strip()

reqs = [line.strip() for line in open('requirements.txt')]

setup(
    name                 = "cc-plugin-sgrid",
    version              = version(),
    description          = "SGRID plugin for the IOOS Compliance Checker Plugin",
    long_description     = readme(),
    license              = 'Apache License 2.0',
    author               = "Kyle Wilcox",
    author_email         = "kyle@axiomdatascience.com",
    url                  = "https://github.com/ioos/cc-plugin-sgrid",
    packages             = find_packages(),
    install_requires     = reqs,
    classifiers          = [
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering'
        ],
    entry_points         = {
        'compliance_checker.suites': [
            'sgrid-1.0.0 = cc_plugin_sgrid.checker_100:SgridChecker100',
        ]
    }
)
