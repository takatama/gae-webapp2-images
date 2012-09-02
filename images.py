import cgi
import webapp2
import urllib
import json

from google.appengine.ext import db
from google.appengine.api import images

class Photo(db.Model):
    data = db.BlobProperty()
    width = db.IntegerProperty()
    height = db.IntegerProperty()
    format = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('<html><body>')
        self.response.out.write("""
            <html><body>
            <form action="/image" enctype="multipart/form-data" method="post">
                <div><input type="file" name="image" /></div>
                <div><input type="submit" /></div>
            </form>
            </body>
            </html>""")
                
def content_type(format):
    if format == images.JPEG:
        return 'image/jpeg'
    elif format == images.PNG:
        return 'image/png'
    elif format == images.WEBP:
        return 'image/webp' 
    elif format == images.BMP:
        return 'image/x-ms-bmp'
    elif format == images.ICO:
        return 'image/vnd.microsoft.icon'
    elif format == images.TIFF:
        return 'image/tiff'
    return None

class Images(webapp2.RequestHandler):
    def get(self):
        image_id = self.request.get('id')
        if image_id:
            image = db.get(image_id)
            if image:
                self.response.headers['Content-Type'] = content_type(image.format)
                self.response.out.write(image.data)
        else:
            self.response.out.write('No image')
    def post(self):
        data = self.request.get('image')
        if data:
            anImage = images.Image(data)
            image = Photo()
            image.data = db.Blob(data)
            image.width = anImage.width
            image.height = anImage.height
            image.format = anImage.format
            anImage.rotate(0)
            anImage.execute_transforms(parse_source_metadata=True)
            exif = anImage.get_original_metadata()
            image.put()
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write("""{
                "id": "%s",
                "width": "%s",
                "height": "%s",
                "format": "%s", 
                "exif": %s
            }""" % (image.key(), image.width, image.height, image.format, json.dumps(exif)))
        else:
            self.response.out.write('No image.')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/image', Images)
], debug=True)

