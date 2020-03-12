"""Setup manifest."""

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="standupstoreparser",
    description="StandUp Store Parser: get fresh updates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.0.1",
    author="Rouslan Gaisin, Timur Odintsov",
    packages=find_packages(),
    entry_points={
        # TODO: # finish this after creating infinite loop for main script
        "console_scripts": [
            "check_events = susp.check_events:main",
        ],
    },
    python_requires='>=3.7',
    url="https://github.com/dvabidonamoloka/standupstoreparser",
)
