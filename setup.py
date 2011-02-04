#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name="micard",
      version="0.0.1",
      description="API wrapper library for micard.com",
      license="MIT",
      author="miCARD LLC",
      #author_email="info@micard.com",
      #url="http://github.com/micard/python-micard",
      install_requires=["oauth", "simplejson"],
      packages = find_packages(),
      keywords= "micard library",
      zip_safe = True)