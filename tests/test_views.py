#
# @author Cory Dolphin
# @wcdolphin
#

from flask.ext.testing import TestCase, Twill
from origiart import db, utils, app
from origiart.models import User,PrescribedUser, Artwork, Type, Style, Medium, FacebookUser
from StringIO import StringIO
import logging
from logging import FileHandler
import twill.commands

class ViewTest(TestCase, Twill):
    viewName = ''
    def create_app(self):
        self.twill = Twill(app)        
        file_handler = FileHandler('loggingFile')
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)
        app.logger.debug('WTFCAKES')
        return app

    def test_basic(self):
        with app.test_client() as c:
            rv = c.get('/%s'%self.viewName)

    def test_post(self):
        with self.twill as t:
            t.browser.go(t.url("/login"))
            twill.commands.formvalue('loginForm','login_username', 'username')
            twill.commands.formvalue('loginForm','login_password','password')
            t.browser.submit()
            print t.browser.get_html()
    
    def login(self,username='email',password='secret'):
        with self.twill as t:
            t.browser.go(t.url('/login'))
            allForms = t.browser.get_all_forms()

            if len(allForms) == 2:
                loginForm = allForms[0]
            else:
                self.fail("There should be two")
                return
            twill.commands.fv('loginForm','login_username',username)
            twill.commands.fv('loginForm','login_password',password)
            t.browser.submit(0)
            t.browser.go(t.url('/login'))

            print t.browser.get_html()

class HomeTest(ViewTest):
    viewName = 'home'
    
    def test_once(self):
        self.test_post()

class BrowseTest(ViewTest):
    viewName = 'browse'
    pass

class ArtistsTest(ViewTest):
    viewName = 'artists'
    pass

class AccountTest(ViewTest):
    viewName = 'account'
    pass

class UploadTest(ViewTest):
    viewName = 'upload'
    pass

class LoginTest(ViewTest):
    viewName = 'login'
    pass

class LogoutTest(ViewTest):
    viewName = 'logout'
    pass


if __name__ == '__main__':
    import unittest
    unittest.main()