Cloud Project
=============


Requirements
------------

	apt-get install python-pip

	pip install -U pip

	pip install -U virtualenvwrapper

	mkdir ~/.virtualenvs

In file .bashrc : 

	export WORKON_HOME="$HOME/.virtualenvs"

	source /usr/local/bin/virtualenvwrapper.sh


- - -

Installation
------------

**Django**

	mkvirtualenv --distribute django1.7

	pip install -r requirements.txt

**Flask**

	workon django1.7

	python install https://github.com/mitsuhiko/flask/tarball/master

In the folder flask-server/ do :

	sqlite3 database < schema.sql

	python

	from server import init_db

	init_db()

- - -

Usage
-----

	workon django1.7

	python django-server/manage.py runserver



- - - 