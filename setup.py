#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="repo2md",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        'console_scripts': [
            'repo2md=repo2md.main:main',
        ],
    },
    python_requires='>=3.6',
)
