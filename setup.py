#!/usr/bin/env python

from distutils.core import setup

setup(name = 'filltex',
      version = '1.1',
      description = 'A LaTeX reference tool',
      long_description = 'A LaTeX reference tool',

      author = 'Davide Gerosa and Michele Vallisneri',
      author_email = 'dgerosa@caltech.edu',
      url = 'https://github.com/dgerosa/filltex',

      py_modules = ['fillbib'],

      scripts = ['bin/fillbib','bin/filltex']
      )
