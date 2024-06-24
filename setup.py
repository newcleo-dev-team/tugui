#!/usr/bin/python3

from setuptools import setup
from setuptools import find_packages
import codecs
import os.path


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_info(rel_path, info):
    for line in read(rel_path).splitlines():
        if line.startswith(f'__{info}__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError(f"Unable to find {info} string.")


if __name__ == '__main__':

    setup(
        name='tugui',
        version=get_info('tugui/__init__.py', 'version'),
        packages=find_packages(),
        include_package_data=True,
        author=get_info('tugui/__init__.py', 'author'),
        author_email='davide.manzione@newcleo.com, '
                     'elena.travaglia@newcleo.com, '
                     'daniele.tomatis@newcleo.com',
        description='Python GUI to support post-processing of results '
                    'obtained with TRANSURANUS fuel performance code',
        long_description_content_type='text/x-rst',
        long_description=open('README.rst', 'r').read(),
        license='lgpl v3',
        python_requires='>=3.11',
        install_requires=['ttkthemes>=3.2.2', 'pandas>=1.5.3',
                          'matplotlib>=3.6.3', 'sphinx>=5.3.0',
                          'sphinx-rtd-theme>=1.2.0', 'myst-parser>=0.18.1',
                          'sphinxcontrib-bibtex>=2.5.0'],
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Physics",
            "Topic :: Scientific/Engineering :: Visualization",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Software Development :: User Interfaces",
        ],
    )