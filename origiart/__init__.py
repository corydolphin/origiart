#
# @author Cory Dolphin
# @wcdolphin
#

from flask import Flask, render_template, request, redirect, url_for, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import (LoginManager,AnonymousUser)
from flask.ext.bcrypt import Bcrypt
from flaskext.cache import Cache
import config #our super sweet configuration module!
from datetime import datetime
app = Flask(__name__)

__cfg = config.getConfig()
app.config.from_object(__cfg) 
app.configType = __cfg

db = SQLAlchemy(app) #database and ORM
loginManager = LoginManager() #handle login and sessions
crypt = Bcrypt(app) #bcrypt for password hashing
BCRYPTDATE = datetime(2012,05,25) #the day we switched to using bcrypt instead of sha1 salt
cache = Cache(app)

loginManager.setup_app(app)
loginManager.login_view = "login"
loginManager.login_message = u"Please log in to access this page."
loginManager.refresh_view = "reauth"
loginManager.session_protection = "strong"
app.jinja_env.autoescape = True

def url_static(filename=None):
	if app.config['DEBUG']:
		return url_for('static',filename=filename)
	return "//s3.amazonaws.com/origiart/static/%s"%filename


app.jinja_env.globals.update(url_static=url_static)

from origiart import views