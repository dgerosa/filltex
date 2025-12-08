#!/usr/bin/env python

# rm -rf dist/ build/ *.egg-info
# python -m build
# twine upload dist/*

from distutils.core import setup

setup(name = 'filltex',
      version = '1.7.4',
      description = 'Automatic queries to ADS and InSPIRE databases to fill LATEX bibliography',
      long_description="See: `github.com/dgerosa/filltex <https://github.com/dgerosa/filltex>`_." ,
      author = 'Davide Gerosa and Michele Vallisneri',
      author_email = 'davide.gerosa@unimib.it',
      url = 'https://github.com/dgerosa/filltex',
      license='MIT',
      py_modules = ['fillbib'],
      scripts = ['bin/fillbib','bin/filltex'],
      include_package_data=True,
      zip_safe=False
      )
