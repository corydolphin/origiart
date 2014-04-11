#
#
# @author Cory Dolphin
# @wcdolphin
#
#

from origiart import app
import models 
from boto.s3.bucket import Bucket
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from PIL import Image
import re
import StringIO
import facebook

def getFacebookUserObj(request):
    return facebook.get_user_from_cookie(request.cookies, app.config['FACEBOOK_APP_ID'], app.config['FACEBOOK_APP_SECRET'])

def uploadFile(aFile,path,callBack = None, bucket=app.config['BUCKET'], public=True, metaData =('Content-Type', 'image/png'),cb=None):
    '''
    Handle file uploads to S3, defaulting to the configured bucket, and to public ACL status
    #TODO: evaluate success of invocation? Was it usccesful?
    '''
    conn = S3Connection(app.config['AWS_KEY'],app.config['AWS_SECRET'])
    b = conn.create_bucket(bucket)
    k = Key(b)
    k.key = path
    if metaData:
        k.set_metadata(*metaData)

    k.set_contents_from_file(aFile, rewind=True, cb=cb)
    if public:
        k.set_acl('public-read')


def deleteFile(path,bucket=app.config['BUCKET']):
    '''
    Delets a particular file on S3 from the current default bucket
    '''
    conn = S3Connection(app.config['AWS_KEY'],app.config['AWS_SECRET'])
    b = conn.create_bucket(bucket)
    b.delete_key(path)

def uploadArtwork(artwork,_file):
    '''
    Uploads a file to S3 in accordance with the model artwork's id, etc.
    TODO: add error checking and test to ensure file was succesfully uploaded
    '''
    try:
        orig = Image.open(_file)
    except IOError:
        return False

    aspectRatio = float(orig.size[0])/orig.size[1] #width over height
    output = StringIO.StringIO()
    orig.save(output, format="PNG")
    uploadFile(output, artwork.imageOriginalPartial)


    homeSlider= orig.resize([ 400,int(400/aspectRatio)],Image.ANTIALIAS)
    output = StringIO.StringIO()
    homeSlider.save(output, format="PNG")
    uploadFile(output, artwork.imageSliderPartial)


    if aspectRatio > 1: #width is larger
        artPage = orig.resize([460,int(460/aspectRatio)],Image.ANTIALIAS)
    else:
         artPage = orig.resize([int(460*aspectRatio),460],Image.ANTIALIAS)
    output = StringIO.StringIO()
    artPage.save(output, format="PNG")
    uploadFile(output, artwork.imageArtPartial, public=True)


    thumb = orig.resize([int(200*aspectRatio),200],Image.ANTIALIAS)
    output = StringIO.StringIO()
    thumb.save(output, format="PNG")
    uploadFile(output, artwork.imageThumbPartial)

    return True

def uploadProfileImage(user,_file):
    '''
    Uploads a file to S3 in accordance with the model artwork's id, etc.
    TODO: add error checking and test to ensure file was succesfully uploaded
    '''
    try:
        orig = Image.open(_file)
    except IOError:
        return False

    aspectRatio = float(orig.size[0])/orig.size[1] #width over height
    output = StringIO.StringIO()
    orig.save(output, format="PNG")
    uploadFile(output, user.imagePartial)

    thumb = orig.resize([210,int(210*aspectRatio)],Image.ANTIALIAS)
    output = StringIO.StringIO()
    thumb.save(output, format="PNG")
    uploadFile(output, user.imageThumbPartial)

    return True

def deleteUploadedArtwork(artwork):
    '''
    Deletes images uploaded for an artwork object, useful in debugging
    '''
    deleteFile(artwork.imageOriginalPartial)
    deleteFile(artwork.imageThumbPartial)
    deleteFile(artwork.imageArtPartial)
    deleteFile(artwork.imageSliderPartial)


def firstOrNone(aList):
    '''
    Simple helper to return first element of a list if it is the only element
    '''
    return aList[0] if len(aList) == 1 else  None

def intOrNone(aStr):
    '''
    Simple helper to cast to an int, returning an int or None, rather than an error
    '''
    if isinstance(aStr,int):
        return aStr
    try:
        return int(aStr)
    except (TypeError, ValueError) as ve:
        return None