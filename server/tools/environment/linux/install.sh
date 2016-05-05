#!/bin/sh
export py=python

apt-get install --yes python-dev
apt-get install --yes python-pip
pip install --upgrade --yes setuptools
apt-get install --yes libmysqld-dev
apt-get install --yes uwsgi-plugin-python
apt-get install --yes swig
apt-get install --yes libssl-dev
apt-get install --yes pylint
apt-get install --yes mysql-server mysql-client
apt-get install --yes libfreetype6-dev

pip install setuptools==18.0.1


cd ../../linux
pip install -r requirements.txt


