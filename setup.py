from setuptools import setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='irreceiver',
      version='0.9.1',
      description='A module to parse the NEC IR remote control protocol in Python',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/computersarecool/irreceiver',
      author='Willy Nolan',
      author_email='contact@interactiondepartment.com',
      license='MIT',
      packages=['irreceiver'],
      zip_safe=False)
