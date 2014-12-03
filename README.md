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



- - -

Usage
-----

	mkvirtualenv --distribute django1.7

	python django-server/manage.py runserver


- - - 