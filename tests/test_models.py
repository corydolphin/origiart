import os
import types
import unittest
from origiart import db, utils
from origiart.models import User,PrescribedUser, Artwork, Type, Style, Medium, FacebookUser
import json
from PIL import Image
import time

def timeit(method):
    '''
    A simple decorator to time a function
    '''
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r %r %2.4f sec' % (args, method.__name__ , te-ts)
        return result

    return timed

class TypeTestCase(unittest.TestCase):
    '''A simple test for Type, essentially a placeholder, more will be added as necessary'''
    def setUp(self):
        pass 
    
    def tearDown(self):
        pass

    @timeit
    def test_query_all(self): 
        tests =Type.query.all()
        assert tests != None
        assert len(tests) !=0

class MediumTestCase(unittest.TestCase):
    '''A simple test for Medium, essentially a placeholder, more will be added as necessary'''
    def setUp(self):
        pass 
    
    def tearDown(self):
        pass
    
    @timeit            
    def test_query_all(self): 
        mediums =Medium.query.all()
        assert mediums != None
        assert len(mediums) !=0

class StyleTestCase(unittest.TestCase):
    '''A simple test for Style, essentially a placeholder, more will be added as necessary'''
    def setUp(self):
        pass 
    
    def tearDown(self):
        pass

    @timeit 
    def test_query_all(self): 
        styles =Style.query.all()
        assert styles != None
        assert len(styles) !=0

class FacebookUserTestCase(unittest.TestCase):
    '''A simple test for Style, essentially a placeholder, more will be added as necessary'''
    def setUp(self):
        pass 
    
    def tearDown(self):
        pass

    @timeit        
    def test_query_all(self): 
        fbUsers =FacebookUser.query.all()
        assert fbUsers != None
        assert len(fbUsers) !=0

class UserTestCase(unittest.TestCase):
    '''A simple test for Users, essentially a placeholder, more will be added as necessary'''
    def setUp(self):
        pass 
    
    def tearDown(self):
        pass
    
    @timeit
    def test_query_all(self): 
        users =User.query.all()
        assert users != None
        assert len(users) !=0

    @timeit
    def test_create(self):
        
        dbUser = User.query.filter(User.email=='email@email.com').first() 
        if dbUser: #cleanup old test
            db.session.delete(dbUser)
            db.session.commit() 
        user = User('email@email.com','joebloe', plainTextPassword='secret')
        db.session.add(user)
        db.session.commit()     
        dbUser = User.query.filter(User.email=='email@email.com').first()
        assert dbUser
        assert dbUser.validatePassword('secret')
        assert not dbUser.validatePassword('notTheSecret')
        db.session.delete(dbUser)
        db.session.commit()
        dbUser = User.query.filter(User.email=='email@email.com').first()
        assert dbUser == None
        
class ArtworkTestCase(unittest.TestCase):
    '''A simple test for Users, essentially a placeholder, more will be added as necessary'''
    def setUp(self):
        pass 
    
    def tearDown(self):
        pass

    @timeit
    def test_artwork_query_all(self): 
        artwork =Artwork.query.all()
        assert artwork != None
        assert len(artwork) != 0
    
    @timeit    
    def test_artwork_create(self):
        dbArtwork = Artwork.query.filter(Artwork.name =='ooblegoogleboogleshrooodlepoodle').first() 
        if dbArtwork:
            db.session.delete(dbArtwork)
            db.session.commit() 
        artwork = Artwork(16,'ooblegoogleboogleshrooodlepoodle',22,styleId='1', description='Something', typeId='1',mediumId=1,supportTypeId=1,height='22',width='33',framed=1)
        db.session.add(artwork)
        db.session.commit() 
        dbArtwork = Artwork.query.filter(Artwork.name =='ooblegoogleboogleshrooodlepoodle').first() 
        assert dbArtwork
        db.session.delete(artwork)
        db.session.commit() 
        dbArtwork = Artwork.query.filter(Artwork.name =='ooblegoogleboogleshrooodlepoodle').first() 
        assert dbArtwork == None

    '''Takes too long
    @timeit
    def test_artwork_upload(self):

        dbArtwork = Artwork.query.filter(Artwork.name =='ooblegoogleboogleshrooodlepoodle').first() 
        if dbArtwork:
            db.session.delete(dbArtwork)
            db.session.commit() 

        artwork = Artwork(16,'ooblegoogleboogleshrooodlepoodle',22,styleId='1', description='Something', typeId='1',mediumId=1,supportTypeId=1,height='22',width='33',framed=1)
        db.session.add(artwork)
        db.session.commit() 
        image = Image.open('tests/example.jpg')
        utils.uploadArtwork(artwork,file('tests/example.jpg'))
        utils.deleteUploadedArtwork(artwork)
        db.session.delete(artwork)
        db.session.commit()
    '''

if __name__ == '__main__':
    unittest.main()
