#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=8.0', ]

test_requirements = ['pytest>=6', ]

setup(
    author="Thomas TJ Dau",
    author_email='thomasdaucd@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="Python project for a custom table top system with a complicated magic system.",
    entry_points={
        'console_scripts': [
            'kbr_char=kbr_char.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='kbr_char',
    name='kbr_char',
    packages=find_packages(include=['kbr_char', 'kbr_char.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/padilin/kbr_char',
    version='0.0.1',
    zip_safe=False,
)
