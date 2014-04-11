from origiart import app, loginManager, crypt, db, BCRYPTDATE, cache
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify, flash
from flask.ext.sqlalchemy import SQLAlchemy
from origiart.models import User,PrescribedUser, Artwork, Type, Support, Medium, Style, Tag, AuthenticationException
from flask.ext.login import (current_user, login_required,login_user,
                     logout_user, confirm_login, fresh_login_required)
from datetime import datetime
import time
from origiart.forms import (LoginForm, RegistrationForm, UploadForm, ImageUploadForm, UpdateProfileForm, UpdateProfileFormFull)
import utils
import facebook

@loginManager.user_loader
def load_user(id):
     return User.getById(id)

@app.route('/', methods=['GET', 'POST'] )
def index():
    if request.method == 'POST':
        if request.form.get('email'): #TODO: convert to using form object
            email = request.form['email']
            ip_address = request.remote_addr
            success = PrescribedUser.prescribeEmail(email,ip_address)
            app.logger.debug("Registered %s as PrescribedUser: Successful?: %s " % (email,success))
            return render_template('launch.html', success=success,email=email)
    return render_template('launch.html')

@app.route('/home')
def home():
    artwork = Artwork.reviewedArt().order_by(Artwork.created_on).limit(10).all()
    return render_template('home.html', recentArtwork = artwork)

@app.route('/browse')
def browse():
    start = time.time()
    filterType = utils.intOrNone(request.args.get('type',None))
    filterMedium = utils.intOrNone(request.args.get('medium',None))
    mediums = Medium.all()
    styles = Style.all()
    types = Type.all()
    supports = Support.all()
    baseQuery = Artwork.reviewedArt().order_by(Artwork.created_on)
    if filterType:
        baseQuery = baseQuery.filter(Artwork.type == filterType)
    if filterMedium:
        baseQuery = baseQuery.filter(Artwork.medium == filterMedium)
    
    artwork = baseQuery.all()
    app.logger.debug('Queries took: %fs' % (time.time() - start) )
    return render_template('browse.html', artwork=artwork, numArts = len(artwork), mediums=mediums,styles=styles,types=types,supports=supports, filterType=filterType, filterMedium=filterMedium)

@app.route('/_browse')
def _browse():
    type = request.args.get('type', -1, type=int)
    medium = request.args.get('medium', -1, type=int)
    art = Artwork.reviewedArt().all()
    return jsonify(arts=[a.json() for a in art])

@app.route('/_tags')
def _browse():
    tags = Tag.all()
    return jsonify(tags=[t.json() for t in tags])

@app.route('/artists')
@app.route('/artist/<string:username>')
def artists(username=None):
    if username: #browse directly to a user's artist page
        user = User.getByUsername(username)
        if user:
            return render_template('artist.html',artist=user)
        else: #general, view all artists page
            app.logger.debug("Invalid artist's page accessed:{%s}" % username)
            return 'error, artist does not exist!' #TODO: Better error
    else:
        artists = User.query.filter(User.has_image==True).all()
        return render_template('artists.html',artists=artists)

@app.route('/artist/<string:username>/<string:artworkUrlName>') #automatically parses and rewrites url
def artwork(username,artworkUrlName=None): #TODO: better formatting of artworkName, %20 is horrible looking
    user = User.getByUsername(username)
    if user:
        artpiece = Artwork.query.filter(Artwork.user_id == user.id).filter(Artwork.url_name == artworkUrlName).first_or_404()
        return render_template('artpiece.html',artpiece=artpiece)
    else:
        app.logger.debug("Invalid artpiece page accessed:{username:%s, artworkName:%s}" % (username,artworkName))
        return 'error, artwork does not exist' #TODO: Better error

@app.route('/cart')
def shoppingCart():
    return "soonCart"

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if current_user.is_oauth_user:
        updateProfileForm = UpdateProfileForm()
    else:
        updateProfileForm = UpdateProfileFormFull()
        
    if request.method == 'POST':
        if updateProfileForm.validate_on_submit():
            if updateProfileForm.hasImage():
                app.logger.debug('We think we have an image')
                current_user.uploadProfileImage(updateProfileForm.updatedProfileImage.data)


    return render_template('account.html',form=updateProfileForm)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    errors = None
    if request.method == 'POST':
        uploadForm = UploadForm(request.form, csrf_enabled=False)
        try:
            if uploadForm.validate_on_submit():
                app.logger.debug('validated')
                if utils.uploadArtwork(uploadForm.artwork,uploadForm.artworkImage.data):
                    return redirect(uploadForm.artwork.link)
                else:
                    flash('There was an error uploading your image, please try again')
            else:
                app.logger.debug('failed to validate:<%s>'%uploadForm.errors)
        except ValueError as ve:
            errors=['%s'%ve]
    mediums = Medium.all()
    styles = Style.all()
    types = Type.all()
    supports = Support.all()
    return render_template('uploadNew.html', mediums=mediums,styles=styles,types=types,supports=supports, errors=errors)

@app.route('/admin')
@login_required
def admin():
    return 'admin'

@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.debug('%s login %s'% (request.method, request.form))
    oauth_user = None
    fbUserObj = utils.getFacebookUserObj(request)
    
    if fbUserObj:
        oauth_user = User.getUserByFacebookUserObj(fbUserObj)
        if not oauth_user:
            try:
                oauth_user = User.createFromFacebookUserObj(fbUserObj)
            except AuthenticationException as ae:
                flash(ae.args[0]['message'],)

    if oauth_user != None:
        login_user(oauth_user)
    
    if current_user.is_authenticated():
        current_user.updateLastActive()
        return redirect(request.args.get('next',url_for('home')))

    if request.method == "POST" and "login_username" in request.form:
        loginForm = LoginForm(request.form, csrf_enabled=False)
        if loginForm.validate():
            login_user(loginForm.user)
            current_user.updateLastActive()
            return redirect(request.args.get('next',url_for('home'))) #check for nextUrl or default to Home
        else:
            for field,errors in loginForm.errors.iteritems():
                for error in errors:
                    flash(error,"login_error")

    elif request.method == "POST" and "reg_email" in request.form:
        registerForm = RegistrationForm(request.form, csrf_enabled=False)
        if registerForm.validate():
            login_user(registerForm.user)
            current_user.updateLastActive()
            return redirect(url_for('home'))
        else:
            for field,errors in registerForm.errors.iteritems():
                for error in errors:
                    flash(error,"register_error")    
    return render_template('login.html')

@app.route('/logout')
def logout():
    if current_user.is_authenticated():
        name = current_user.displayName
        logout_user()
        return redirect(url_for('home'))
    else:
        return "why are you trying to log out? You aren't logged in"

@app.route('/mu-c9d98459-e81972b2-54d297df-5e25108c')
@app.route('/mu-54eddf28-cca62181-96e07c8e-6fce23ee')
def blitz():  #handle blitz.io authentication for testing
    return '42'

@app.route('/google2933ab7318d9ba0f.html')  #TODO: proper extension? Autocorrect appropriately throughout 
def googleSiteVerification():
    return 'google-site-verification: google2933ab7318d9ba0f.html'


@app.errorhandler(404)
def page_not_found(error):
    return 'Cory should really handle this page_not_found'


@app.errorhandler(403)
def forbidden(error):
    return 'Cory should really handle this forbidden'


@app.errorhandler(500)
def internal_server_error(error):
    return 'Cory should really handle this internal server error'

