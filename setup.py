# from distutils.core import setup
from setuptools import setup, find_packages
setup(name='resttools',
      version='1.0',
      description='UW-IT REST library',
      packages=find_packages(),
      include_package_data=True,
      )
