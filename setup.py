# coding=utf-8
# type: ignore
__version__ = '1.0.0'
from setuptools import setup, find_packages

# README read-in
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
# END README read-in

setup(
    name='git-credentials',
    version=__version__,
    packages=['git_credentials'],
    package_data={'git_credentials': ['py.typed']},
    description='Simple library to interact with Git Credentials',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/theCapypara/python-git-credentials/',
    author='Marco "Capypara" Köpcke',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
)
