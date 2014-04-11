#
# @author Cory Dolphin
# @wcdolphin
#

from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from flask.ext.urls import permalink
from origiart import db, app, cache, url_static, crypt
import datetime
import utils
import re
import facebook

class SimpleModel(object):

    @classmethod
    def getByName(cls,name):
        ''' Common method to get a simple model (i.e. Tag, Type, etc) by name'''
        if name == None or len(name) == None:
            raise ValueError("Name must be defined and of non-zero length")
        return cls.query.filter(cls.name == name).first()

    @classmethod
    @cache.memoize(600)
    def getById(cls,id):
        return cls.query.filter(cls.id == id).first()

    @classmethod
    @cache.memoize(600)
    def all(cls):
        return cls.query.all()

class Jsonable(object):
    '''
    Jsonable mixin class to provide json functionality and a number of simple helpers
    '''
    @staticmethod
    def _objHook(obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        if isinstance(obj, Jsonable):
            return Jsonable.json()
        else:
            return obj

    @staticmethod
    def _typeHook(typeObj):
        return typeObj in [bool, str, int, float, Jsonable, datetime.datetime]

    def json(self, objHook=lambda x: Jsonable._objHook(x), typeHook=lambda x: Jsonable._typeHook(x)):
        if not hasattr(self, '__jsonattrs__'):
            attrList = []
            for k, v in self.__dict__.iteritems():
                if typeHook(type(v)):
                    attrList.append(k)
            self.__jsonattrs__ = attrList
        return {attr: objHook(getattr(self, attr)) for attr in self.__jsonattrs__}

    def __str__(self):
        return str(self.json())

    @classmethod
    def getId(cls,obj): #TODO: fix implementation or remove
        '''
        @deprecated
        Returns the id of a given model instance by intelligently checking the chain
        of options to search and or query the model class by: casting to int, returing
        int attribute, or by filtering by object name
        '''
        if isinstance(obj, int):
            return obj
        if isinstance(obj, self.__class__):
            return obj.id
        if isinstance(obj, str):
            try:
                return int(obj)
            except ValueError as ve:
                pass#ignore error
            name_obj = cls.query.filter(self.__class__.name == obj).first()
            return name_obj.id if name_obj else None

class User(db.Model, Jsonable):
    '''
    This object represents a registered user
    '''
    __tablename__ = 'users'
    __jsonattrs__ = ['id','email','username','full_name','joined_on','last_active','is_artist','slogan','city','state','description']
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40))
    username = db.Column(db.String(40))
    password = db.Column(db.String(40))
    full_name = db.Column(db.String(40))    
    joined_on = db.Column(db.DateTime)
    last_active = db.Column(db.DateTime)    
    is_artist = db.Column(db.Boolean)
    slogan = db.Column(db.String(60))
    location = db.Column(db.String(50))
    description = db.Column(db.Text)
    has_image = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)
    __artworks = relationship('Artwork', lazy="dynamic")
    is_oauth_user = db.Column(db.Boolean)
    

    def __init__(self, email, username, full_name = None, plainTextPassword = None, slogan=None, description=None, is_oauth_user = False):
        self.email = email
        self.username = username
        self.full_name = full_name
        if plainTextPassword: #TODO: need to architect better solution to handling pws. Want to enforce reqs here
            self.password = crypt.generate_password_hash(plainTextPassword)

        self.joined_on = datetime.datetime.now()
        self.is_admin = False
        self.has_image = False
        self.slogan = slogan
        self.description = description
        self.is_oauth_user = is_oauth_user

    def __repr__(self):
        return '{User %r}' % self.username

    @property
    @permalink
    def link(self):
        '''
        Returns the url for this User's Artist page by passing username param to the artists view
        '''
        return 'artists', {'username': self.username}



    @property
    def __imageBaseurl(self):
        '''
        Private helper to return the basis for all image urls
        #TODO: support https?
        '''
        return "http://s3.amazonaws.com/%s/%s" % (app.config['BUCKET'], self.__partial)

    @property
    def __partial(self):
        '''
        Private helper to return the path to this file relative to the root of S3
        '''
        return "user_uploads/%s/%s" % (self.id, self.id)

    @property
    def imageThumb(self):
        '''
        Returns the url for this User's thumbnail image
        '''
        if self.has_image:
            return  "%s.thumb.png" % self.__imageBaseurl
        else:
            return url_static(filename='img/defaultProfile.thumb.png')
    @property
    def imageThumbPartial(self):
        '''
        Returns the path to this artwork's original image relative to the root of S3
        '''
        return  "%s.thumb.png" % self.__partial
    
    @property
    def imagePartial(self):
        '''
        Returns the path to this artwork's original image relative to the root of S3
        '''
        return  "%s.png" % self.__partial

    @property
    def image(self):
        '''
        Returns the url for this User's full bleed image
        '''
        if self.has_image:
            return  "%s.png" % self.__imageBaseurl
        else:
            return url_static(filename='img/defaultProfile.png')

    @property
    def tempImagePartial(self):
        '''
        Returns the path to this artwork's original image relative to the root of S3
        '''
        return  "%s.temp.png" % self.__partial

    @property
    def tempImage(self):
        '''
        Returns the url for this User's full bleed image
        '''
        if self.has_image:
            return  "%s.temp.png" % self.__imageBaseurl
        else:
            return url_static(filename='img/defaultProfile.png')

    @property
    def tempArtPartial(self):
        '''
        Returns the path to this artwork's original image relative to the root of S3
        '''
        return  "%s.tempart.png" % self.__partial

    @property
    def tempArt(self):
        '''
        Returns the url for this User's full bleed image
        '''
        if self.has_image:
            return  "%s.tempart.png" % self.__imageBaseurl
        else:
            return url_static(filename='img/defaultProfile.png')

    @property
    def displayName(self):
        '''
        Return's this user's display name, either their full name, if set,
        or else defaults to username
        '''
        return self.full_name or self.username#default to username if full_name is not set

    @property
    def artworks(self):
        '''
        Provides a simple wrapper for querying the artwork associated with this User object
        '''
        return self.__artworks.filter('artwork.is_reviewed=True') #need more elegant solution

    def get_id(self):
        '''
        Stub boilerplate methods required for use with Flask-Login 
        '''
        return self.id

    def is_active(self):
        '''
        Stub boilerplate methods required for use with Flask-Login 
        '''
        return True

    def is_anonymous(self):
        '''
        Stub boilerplate methods required for use with Flask-Login 
        '''        
        return False

    def is_authenticated(self):
        '''
        Stub boilerplate methods required for use with Flask-Login 
        '''
        return True

    def updateLastActive(self):
        '''
        Updates last date-active to the current time
        '''
        self.last_active = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getByUsername(username):
        '''
        Helper to find Users by username.
        Returns only if there is a single exact case match
        '''
        return utils.firstOrNone(User.query.filter(User.username == username).all())

    @staticmethod
    def getByEmail(email):
        '''
        Helper to find Users by email.
        Returns only if there is a single exact case match
        '''
        return utils.firstOrNone(User.query.filter(User.email == email).all())

    @staticmethod
    def getById(id):
        '''
        Helper to find Users by id.
        Returns only if there is a single exact case match
        '''
        return utils.firstOrNone(User.query.filter(User.id == id).all())

    @staticmethod
    def queryById(id):
        '''
        Helper to query Users by Id, simply reducing the length of method call
        '''
        return User.query.filter(User.id == id)

    @staticmethod
    def queryByUsername(username):
        '''
        Helper to query Users by username, simply reducing the length of method call
        '''
        return User.query.filter(User.username == username)

    @staticmethod
    def getUserByFacebookUserObj(fbUserObj):
        '''
        Returns a User using Facebook, needs to be refactored
        '''
        if fbUserObj and 'uid' in fbUserObj.keys():
            fbUser = FacebookUser.getByOAuthId(fbUserObj['uid'])
            if fbUser != None:
                return fbUser.user
        return None

    @staticmethod
    def createFromFacebookUserObj(fbUserObj):
        '''
        Creates a new User based upon a FacebookUserObject returned by the JavaScript API,
        stored in cookies
        '''
        if fbUserObj and 'access_token' in fbUserObj.keys():
            graph = facebook.GraphAPI(fbUserObj['access_token'])
            profile = graph.get_object("me")
            app.logger.debug(profile)
            if User.getByEmail(profile['email']):
                raise AuthenticationException({'message':'This email is already associated with an account'}) #TODO: properly ensure there is a way to continue
            _user = User(email = profile['email'], username = "%s %s" % (profile['first_name'], profile['last_name']))
            db.session.add(_user)
            db.session.commit()
            user = User.getByEmail(profile['email'])
            if user:
                fbUser = FacebookUser(fbUserObj['uid'], user.id)
                db.session.add(fbUser)
                db.session.commit()
                fbUser = FacebookUser.getByOAuthId(fbUserObj['uid'])
                if fbUser:
                    return fbUser.user
                else:
                    return None #we should clean up from the mistake here

    def uploadProfileImage(self,_file):
        utils.uploadProfileImage(self, _file)

    def updatePassword(self,plainTextPassword):
        self.password = crypt.generate_password_hash(plainTextPassword)
        db.session.commit()

    def validatePassword(self,plainTextPassword):
        return crypt.check_password_hash(self.password,plainTextPassword)

class PrescribedUser(db.Model,Jsonable):
    '''
    This object represents a user who is signed up for emails_prescribe
    '''
    __tablename__ = 'emails_prescribe'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    ip_address = db.Column(db.String(16))
    created_on = db.Column(db.DateTime)

    def __init__(self, email, remoteAddress, created_on=None):
        self.email = email
        self.ip_address = remoteAddress
        self.created_on = created_on or datetime.datetime.now()

    def __repr__(self):
        return '<PrescribedUser %r>' % self.email

    @staticmethod
    def prescribeEmail(email, remoteAddress):
        '''
        Attempts to prescribe an email address to the mailing list,
        will return Boolean of success.
        '''
        try:
            pu = PrescribedUser(email,remoteAddress)
            db.session.add(pu)
            db.session.commit()
            return True
        except Exception,e:
            return False


class Type(db.Model,Jsonable, SimpleModel):
    '''
    Simple ArtworkType model
    '''
    __tablename__='artwork_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.Text)

    def __repr__(self):
        return '{Type %r}' % self.name

    @staticmethod
    def getOrCreateByName(name):
        pass

    @staticmethod
    def getByName(name):
        return self.__

class Medium(db.Model,Jsonable, SimpleModel):
    '''
    Simple ArtworkMedium model
    '''
    __tablename__='artwork_mediums'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.Text)
    def __repr__(self):
        return '{Medium %r}' % self.name


class Support(db.Model,Jsonable, SimpleModel):
    '''
    Simple ArtworkSupportType model
    '''
    __tablename__='artwork_support_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.Text)

    def __repr__(self):
        return '{Support %r}' % self.name


class Style(db.Model,Jsonable, SimpleModel):
    __tablename__='artwork_styles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.Text)

    def __repr__(self):
        return '{Style %r}' % self.name

class Tag(db.Model,Jsonable, SimpleModel):
    __tablename__='tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))

    def __init__(self,name):
        self.name = name
    def __repr__(self):
        return '{Tag #%r}' % self.name


class Artwork(db.Model,Jsonable):
    __tablename__ = 'artwork'
    __jsonattrs__ = ['style', 'url_name', 'user_id', 'name', 'price', 'support_type', 'height', 'width', 'created_on', 'medium', 'framed', 'type', 'id', 'description']
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    url_name = db.Column(db.String(40))
    name = db.Column(db.String(60))
    price = db.Column(db.Numeric) #TODO: find type or declare new type for postgres::money
    type = db.Column(db.Integer, db.ForeignKey(Type.id))
    medium = db.Column(db.Integer, db.ForeignKey(Medium.id))
    support_type = db.Column(db.Integer, db.ForeignKey(Support.id))
    style = db.Column(db.Integer, db.ForeignKey(Style.id))
    width = db.Column(postgresql.REAL)
    height = db.Column(postgresql.REAL)
    framed = db.Column(db.Boolean)
    created_on = db.Column(db.DateTime)    
    description = db.Column(db.Text)
    is_reviewed = db.Column(db.Boolean)


    user = relationship(User, primaryjoin=(user_id == User.id), lazy="joined") #we can optimize and only grab user_name, later.
    _style = relationship(Style, primaryjoin=(style == Style.id),lazy="joined")
    _medium = relationship(Medium, primaryjoin=(medium == Medium.id),lazy="joined")
    _type = relationship(Type, primaryjoin=(type == Type.id),lazy="joined")
    _support_type = relationship(Support, primaryjoin=(support_type == Support.id),lazy="joined")

    @staticmethod
    def queryByUsername(username):
        return Artwork.query.filter(Artwork.username == username)

    @staticmethod
    def urlFromName(name):
        '''
        Replaces strings of alphanumeric characters with a single underscore 
        '''
        pattern = re.compile('[\W_]+')
        x = pattern.sub('_',name)
        return x if x[len(x)-1] != '_' else x[:-1] #remove trailing underscore

    @property
    def __imageBaseurl(self):
        '''
        Private helper to return the basis for all image urls
        #TODO: support https?
        '''
        return "http://s3.amazonaws.com/%s/%s" % (app.config['BUCKET'], self.__partial)

    @property
    def __partial(self):
        '''
        Private helper to return the path to this file relative to the root of S3
        '''
        return "user_uploads/%s/%s" % (self.user_id, self.url_name)

    @property
    def imageSlider(self):
        '''
        Returns the url for this Artwork's slider page image
        '''
        return  "%s.slider.png" % self.__imageBaseurl

    @property
    def imageSliderPartial(self):
        '''
        Returns the path to this artwork's slider image relative to the root of S3
        '''
        return  "%s.slider.png" % self.__partial

    @property
    def imageThumb(self):
        return  "%s.thumb.png" % self.__imageBaseurl

    @property
    def imageThumbPartial(self):
        '''
        Returns the path to this artwork's thumbnail image relative to the root of S3
        '''
        return  "%s.thumb.png" % self.__partial

    @property
    def imageArt(self):
        return  "%s.art.png" % self.__imageBaseurl

    @property
    def imageArtPartial(self):
        '''
        Returns the path to this artwork's artwork page image relative to the root of S3
        '''
        return  "%s.art.png" % self.__partial

    @property
    def imageOriginal(self):
        return  "%s.png" % self.__imageBaseurl

    @property
    def imageOriginalPartial(self):
        '''
        Returns the path to this artwork's original image relative to the root of S3
        '''
        return  "%s.png" % self.__partial

    @property
    @permalink
    def link(self):
        '''
        Returns the url for this User's Artist page
        '''
        return 'artwork', { 'username': self.user.username, 'artworkUrlName' : self.url_name}

    @staticmethod
    def reviewedArt():
        '''
        Class function to return query for all artwork which has been reviewed, i.e. for browse
        '''
        return Artwork.query.filter(Artwork.is_reviewed == True)

    def __repr__(self):
        return '{Artwork id=%r name=%r by User{id=%r}}' % (self.id, self.name, self.name)

    @property
    def styleName(self):
        return self._style.name

    @property
    def mediumName(self):
        return self._medium.name

    @property
    def supportTypeName(self):
        return self._support_type.name

    @property
    def typeName(self):
        return self._type.name

    def uploadImage(self,_file):
        '''
        Attempts to upload an image to s3 for this artwork instance, returning the result
        '''
        self.has_image = utils.uploadArtwork(self, _file)
        db.session.commit()
        return self.has_image
    
    def __init__(self, user_id, name, price, description = None, styleId = None, typeId = None, mediumId = None, supportTypeId = None, height = None, width = None,  framed = None):
        self.id = None  #will be generated
        self.created_on = datetime.datetime.now()  #defaulted to NOW
        self.user_id = user_id
        self.name = name
        self.url_name = Artwork.urlFromName(self.name)
        self.price = price

        self.style = styleId
        self.support_type = supportTypeId
        self.type = typeId
        if not mediumId: mediumId = 1 #fix with a smart default
        self.medium = mediumId
        self.height = utils.intOrNone(height)
        self.width = utils.intOrNone(width)
        self.framed = True if framed == '1' or framed == True else False
        self.description = description


class FacebookUser(db.Model,Jsonable):
    __tablename__ = 'fb_users'
    oauth_uid = db.Column(db.Text, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = relationship(User, primaryjoin=(user_id == User.id), lazy="joined")

    def __repr__(self):
        return '{FacebookUser %s}' % self.user

    @staticmethod
    def getByOAuthId(oauth_uid):
        return utils.firstOrNone(FacebookUser.query.filter(FacebookUser.oauth_uid == oauth_uid).all())

    def __init__(self,oauth_uid,user_id):
        self.oauth_uid = oauth_uid
        self.user_id = user_id


class AuthenticationException(Exception):
    pass