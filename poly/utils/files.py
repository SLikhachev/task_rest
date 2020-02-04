
import os
import string
from secrets import choice 
from flask import request, redirect, url_for, send_from_directory
from flask import current_app
from flask_restful import Resource
from werkzeug import secure_filename
from poly.utils.uploadfile import uploadfile


def get_name_tail(nchars):
    alphabet = string.ascii_letters + string.digits
    return ''.join(choice(alphabet) for i in range(nchars))

def allowed_file(filename, config):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in config['ALLOWED_EXTENSIONS']

"""
def create_thumbnail(image):
    try:
        base_width = 80
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image))
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
        img.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image))

        return True

    except:
        print traceback.format_exc()
        return False
"""

class FileMixin:
    
    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

    def gen_file_name(self, catalog, filename):
        """
        If file was exist already, rename it and return a new name
        """
        i = 1
        while os.path.exists(os.path.join(catalog, filename)):
            name, extension = os.path.splitext(filename)
            filename = '%s_%s%s' % (name, str(i), extension)
            i += 1
        return filename


class ListDir(Resource, FileMixin):
    
    def get(self, dir, subdir):
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], dir, subdir)         
        print(current_app.config['UPLOAD_FOLDER'])
        print(catalog)
        files = [ f for f in os.listdir(catalog) \
            if os.path.isfile( os.path.join(catalog, f) ) and f not in current_app.config['IGNORED_FILES'] ]
        file_display = []

        for f in files:
            size = os.path.getsize(os.path.join(catalog,f))
            file_saved = uploadfile(name=f, size=size)
            file_display.append(file_saved.get_file())

        return { "files": file_display }

class TakeFile(Resource, FileMixin):
    
    def get(self, dir, subdir, filename):
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], dir, subdir) #, filename)
        #absa = os.path.join(current_app.root_path, filename)
        #size = os.path.getsize(catalog)
        #return { "cat": catalog, "root": current_app.root_path } #, "absa": absa  }
        
        return send_from_directory(catalog, filename)
    
    def post(self, dir, subdir):
        files = request.files['file']
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], dir, subdir)   
        if files:
            filename = secure_filename(files.filename)
            filename = self.gen_file_name(catalog, filename)
            mime_type = files.content_type

            if not self.allowed_file(files.filename):
                result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")
        
            else:
                # save file to disk
                uploaded_file_path = os.path.join(catalog, filename)
                files.save(uploaded_file_path)
                """
                # create thumbnail after saving
                if mime_type.startswith('image'):
                    create_thumbnail(filename)
                """
                # get file size after saving
                size = os.path.getsize(uploaded_file_path)

                # return json for js call back
                result = uploadfile(name=filename, type=mime_type, size=size)
            
            return { "files": [result.get_file()] }, {'Access-Control-Allow-Origin': '*'}

    def delete(self, dir, subdir, filename):
        catalog = os.path.join(current_app.config['UPLOAD_FOLDER'], dir, subdir)
        file_path = os.path.join(catalog, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return {filename: 'True'}
            except:
                return {filename: 'False'}
            
