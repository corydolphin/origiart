Python, Flask, SQLAlchemy, gunicorn and gevent  
============

Rewrite of the application in python (my native tongue) has begun, using the awesome Flask microframework

Instructions
------------

First, you'll need to clone the repo.


Second, download `pip` and `virtualenv`

    $ sudo easy_install pip
    $ sudo pip install virtualenv

Optionally, install `foreman` and `heroku` Ruby Gems

    $ sudo gem install foreman heroku





Now, you can setup an isolated environment with `virtualenv`.

    $ virtualenv --no-site-packages env
    $ source env/bin/activate

On ubuntu, install the necessary packages:
	$sudo apt-get install python-dev 

Next, install the requirements in your isolated python environment.

    $ pip install -r requirements.txt



Now, you can run the application locally.

    $ python run.py

You can also run it using the production server if you install `libevent-dev` and `foreman`, but I am leaving that for another day, it also is difficult in Windows

    $ foreman start
