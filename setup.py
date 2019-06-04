""" Setup script. """

# pylint: disable=exec-used,undefined-variable

from setuptools import find_packages, setup

with open("README.rst", "r") as readme_file:
    README = readme_file.read()

exec(open("src/edo_exp/version.py", "r").read())

setup(
    name="edo_exp",
    version=__version__,
    description="Generic functions for running experiments with `edo`.",
    long_description=README,
    url="https://github.com/daffidwilde/edo_exp",
    author="Henry Wilde",
    author_email="henrydavidwilde@gmail.com",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
)
