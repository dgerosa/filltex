#!/usr/bin/env python

from distutils.core import setup

setup(name = 'filltex',
      version = '1.5.1',
      description = 'Automatic queries to ADS and InSPIRE databases to fill LATEX bibliography',
      long_description="See: `github.com/dgerosa/filltex <https://github.com/dgerosa/filltex>`_." ,
      author = 'Davide Gerosa and Michele Vallisneri',
      author_email = 'dgerosa@star.sr.bham.ac.uk',
      url = 'https://github.com/dgerosa/filltex',
      license='MIT',
      py_modules = ['fillbib'],
      scripts = ['bin/fillbib','bin/filltex'],
      include_package_data=True,
      zip_safe=False
      )
