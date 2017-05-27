""" A setuptools based setup module """

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='peachy',

    # Version (PEP440)
    version='0.1.0',

    description='A python3 game development framework',
    long_description=open('README.rst').read(),

    url='https://github.com/shellbotx/peachy',

    author='Sheldon Allen (shellbot)',
    author_email='studio.shellbot@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End User/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Games/Entertainment',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: pygame',
        'Topic :: Software Development :: Libraries :: Python Modules'
        'Topic :: Software Development :: Version Control :: Git'
    ],

    keywords='peachy pygame gamedev game gaming development 2d graphics',

    packages=find_packages(),
    install_requires=[
        'pygame',
        'pytmx',
        'click'
    ]
)
