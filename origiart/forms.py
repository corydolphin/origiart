#
# @author Cory Dolphin
# @wcdolphin
#

from origiart import db, BCRYPTDATE, app
from origiart.models import User,PrescribedUser, Artwork, Type, Support, Medium, Style, Tag, AuthenticationException
from flask import flash
from flask.ext.wtf import (Form, TextField, Required, PasswordField, validators, FileField,
                                                    file_allowed, file_required)
from flask.ext.login import current_user
from flask.ext.uploads import UploadSet, IMAGES, configure_uploads
from sqlalchemy.exc import IntegrityError
images = UploadSet("images", IMAGES, default_dest=lambda app: '/tmp/flask_photo_ups')
configure_uploads(app, (images))

class LoginForm(Form):
    login_username = TextField(validators=[Required()])
    login_password = TextField(validators=[Required()])
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        self.rv = Form.validate(self)
        if not self.rv:
            return False
        tUser = User.getByUsername(self.login_username.data)
        if tUser ==None: #not a valid username
            tUser = User.getByEmail(self.login_username.data) #check if it is actaully an email address
            if tUser == None: 
                self.login_username.errors.append("The username you have entered does not exist")
                return False
            if tUser.is_oauth_user:
                self.login_username.errors.append("The email you have entered is associated with a Facebook account, please login using Facebook.")

        if not tUser.validatePassword(self.login_password.data):
            self.login_password.errors.append("It seems you have entered an incorrect password")
            return False

        self.user = tUser
        return True


class RegistrationForm(Form):
    reg_username = TextField('username', [validators.Required()])
    reg_email = TextField('Email Address', [validators.Required()])
    reg_password = PasswordField('password', [validators.Required(),validators.Length(min=4, max=100, message="Please enter a password longer than four characters")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None
    
    def validate(self):
        rv = Form.validate(self)
        self.rv = rv

        usernameExists = User.query.filter(User.username== self.reg_username.data).count() != 0
        self.usernameExists = usernameExists
        if usernameExists:
            self.reg_username.errors.append('The username you have selected is already in use')
            return False

        emailExists = User.query.filter(User.email == self.reg_email.data).count() != 0
        self.emailExists = emailExists
        if emailExists:
            self.reg_email.errors.append('The email address you have selected is already in use!') #perhaps we should let users make multiple accounts?
            return False
        if self.rv:
            self.user = User(self.reg_email.data,self.reg_username.data, plainTextPassword = self.reg_password.data)
            db.session.add(self.user)
            db.session.commit()
        return self.rv


class UploadForm(Form):
    artworkImage = FileField("Photo Upload", validators=[file_allowed(images, message="The file you selected does not appear to be an image, please try again or contact support")])

    title = TextField(validators=[Required(),validators.Length(min=app.config['MAX_TITLE_LENGTH'],max=app.config['MAX_TITLE_LENGTH'],
        message="The title must be between %s and %s characters"%
        (app.config['MIN_TITLE_LENGTH'],app.config['MAX_TITLE_LENGTH']))])

    type = TextField(validators=[Required(),validators.Length(min=1, 
        message="You must describe the type of your work")])

    medium = TextField()
    support_type = TextField()
    style = TextField()
    width = TextField()
    height = TextField()

    description = TextField(validators=[Required(),validators.Length(min=4, max=400,
        message="The title must be between %s and %s characters"%
        (app.config['MIN_TITLE_LENGTH'],app.config['MAX_TITLE_LENGTH']))])
    #tags
    
    framed = TextField(validators=[Required(),validators.Length(min=1,
        message="Please tell us if your work is framed")])
    cost = TextField(validators=[Required(),validators.Length(min=1,
        message="You need to tell us how much you want! (remember, you are the one selling )")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.artwork = None

    def validate(self):
        rv = Form.validate(self)
        self.rv = rv
        if not rv:
            return False

        self.artwork = Artwork(current_user.id, self.title.data,
             self.cost.data, styleId = self.style.data,
             supportTypeId = self.support_type.data,typeId = self.type.data,
             height = self.height.data, width = self.width.data, mediumId = self.medium.data,
             framed = self.framed.data, description = self.description.data)

        self.artwork.is_reviewd = app.config['DEBUG']

        try:
            db.session.add(self.artwork)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            app.logger.debug(e)
            return False
       
        return True


class UpdateProfileForm(Form):
    updatedProfileImage = FileField("Photo Upload", validators=[file_allowed(images,
        message="The file you selected does not appear to be an image, please try again or contact support")])
    location = TextField()
    slogan = TextField(validators=[validators.Length(min=0, max=140,
        message="Please keep your slogan short, 140 characters or less, please.")])
    description = TextField(validators=[validators.Length(min=0, max=400,
        message="Please limit your description to 400 characters")])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)


    def hasImage(self):
        return self.updatedProfileImage.data != None

    def validate(self):
        rv = Form.validate(self)
        self.rv = rv
        if not rv:
            return False
        #TODO: this code is repeated, inheritance seemed to break the cleaner version though
        if len(self.slogan.data) and self.slogan.data != current_user.slogan:
            current_user.slogan = self.slogan.data
            flash("Your slogan has been updated","message")
        if len(self.description.data) and self.description.data != current_user.description:            
            current_user.description = self.description.data
            flash("Your description has been updated","message")
        if len(self.location.data) and self.location.data != current_user.location:
            current_user.location = self.location.data
            flash("Your location has been updated","message")

        db.session.commit()  
        return True

class UpdateProfileFormFull(Form):
    updatedProfileImage = FileField("Photo Upload", validators=[file_allowed(images,
        message="The file you selected does not appear to be an image, please try again or contact support")])
    location = TextField()
    slogan = TextField(validators=[validators.Length(min=0, max=140,
        message="Please keep your slogan short, 140 characters or less, please.")])
    description = TextField(validators=[validators.Length(min=0, max=400,
        message="Please limit your description to 400 characters")])
    current_password = TextField(validators=[validators.Length(min=0, max=app.config['PASSWORD_MAX_LENGTH'])])
    user_password = TextField(validators=[validators.Length(min=0, max=app.config['PASSWORD_MAX_LENGTH'])])
    user_password_confirmation = TextField(validators=[validators.Length(min=0, max=app.config['PASSWORD_MAX_LENGTH']),
        validators.EqualTo('user_password', message='The passwords you have entered do not match')])

    @property
    def hasImage(self):
        return self.updatedProfileImage.data != None

    def validate(self):
        self.rv = False
        rv = Form.validate(self)
        self.rv = rv
        if not rv:
            return False


        if len(self.user_password.data) or len(self.user_password_confirmation.data) or len(self.current_password.data): #user has entered a new pw
            if not self.user_password.data == self.user_password_confirmation.data: #not the password
                flash("The passwords you have entered do not match", "error")
                self.rv = False
            if len(self.user_password.data) < app.config['PASSWORD_MIN_LENGTH'] and len(self.user_password.data):
                flash("The new password you have entered is simply too short, please enter a longer password", "error")
                self.rv = False
            if self.rv: #password length sufficient and passwords match
                if current_user.validatePassword(self.current_password.data):
                    current_user.updatePassword(self.user_password)
                    flash("Your password has been updated","message")
                else:
                    flash("It seems you have entered an incorrect password","error")
                    self.rv = False

        if not self.rv: #if we failed to change password, do not process the rest of the form
            return False
        #TODO: this code is repeated, inheritance seemed to break the cleaner version though
        if len(self.slogan.data) and self.slogan.data != current_user.slogan:
            current_user.slogan = self.slogan.data
            flash("Your slogan has been updated","message")
        if len(self.description.data) and self.description.data != current_user.description:            
            current_user.description = self.description.data
            flash("Your description has been updated","message")
        if len(self.location.data) and self.location.data != current_user.location:
            current_user.location = self.location.data
            flash("Your location has been updated","message")

        db.session.commit()  
        return True



class ImageUploadForm(Form):
    '''
    This form aims to generically validate images as image types and mimetypes.
    Pass in the fileFieldName as a parameter in order to adapt it to different forms
    '''
    def __init__(self, fileFieldName='file', *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        setattr(self,fileFieldName,FileField("Photo Upload", validators=[file_required(),
                                    file_allowed(images, "Images only!")]))

    def validate(self):
        rv = Form.validate(self)
        self.rv = rv
        if not rv:
            return False
        return True