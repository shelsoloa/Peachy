""" A setuptools based setup module """

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='peachy',

    # Version (PEP440)
    version='0.0.3',

    description='A python game development framework',
    long_description=open('README.rst').read(),

    # The project's main homepage
    url='https://github.com/shellbotx/peachy',

    author='Sheldon Allen',
    author_email='a.sheldon.sol@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: pygame'
    ],

    keywords='peachy pygame gamedev game gaming development 2d graphics',

    packages=find_packages(),
    install_requires=[
        'pygame'
    ]
)
