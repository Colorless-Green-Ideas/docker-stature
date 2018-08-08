#! /usr/bin/env python

from setuptools import setup
setup(name="stature",
      version="0.2.0b1",
      scripts=['stature.py'],
      author="Jack Laxson",
      author_email="jackjrabbit@gmail.com",
      description="Docker container metadata as a Cachet component data!",
      license="AGPL v3+",
      install_requires=["toml", "click>=6", "cachet==0.1.0", "docker>=3"],
      url="https://github.com/Colorless-Green-Ideas/docker-stature",
      classifiers=["License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
      'Intended Audience :: Developers',
      'Topic :: Utilities','Topic :: System :: Monitoring'])
