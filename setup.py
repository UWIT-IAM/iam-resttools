import os
from setuptools import setup, find_packages

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VERSION_FILE = os.path.join(BASE_DIR, 'resttools', 'VERSION')
with open(VERSION_FILE) as f:
    VERSION = f.readlines()[-1].strip()

setup(name='uw-iam-resttools',
      version=VERSION,
      url='https://github.com/UWIT-IAM/iam-resttools',
      author='UW-IT Identity and Access Management',
      author_email='help@uw.edu',
      description='UW-IT REST library for IAM APIs',
      license='Apache License, Version 2.0',
      packages=find_packages(),
      include_package_data=True,
      install_requires=['lxml', 'python-dateutil', 'urllib3', 'jinja2', 'six']
      )
