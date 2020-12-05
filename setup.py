# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="py-blue-pedal",
    version="0.1.0",
    description="Python library to interact with Bluetooth Lower Energy (BLE) cycling smart trainers and heart rate monitors",
    long_description=readme,
    author="Renato Torres",
    author_email="renato@willful.pt",
    url="https://github.com/willful-it/py-blue-pedal",
    license=license,
    packages=find_packages(exclude=("tests", "docs"))
)
