""" Setup script. """

from setuptools import find_packages, setup

setup(
    name="edo_exp",
    version="0.0.1",
    description="Generic functions for running experiments with `edo`.",
    url="https://github.com/daffidwilde/edo_exp",
    author="Henry Wilde",
    author_email="henrydavidwilde@gmail.com",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
)
