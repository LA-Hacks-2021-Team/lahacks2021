import imghdr
import os
from flask import Flask, render_template, flash, request, redirect, url_for, abort, jsonify
from werkzeug.utils import secure_filename
from flask_dropzone import Dropzone

from main import *

app = Flask(__name__)
dropzone = Dropzone(app)

app.config['MAX_CONTENT_LENGTH'] = 4096 * 4096
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'

app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image'
app.config['DROPZONE_MAX_FILES'] = 1

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0) 
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                file_ext != validate_image(uploaded_file.stream):
            abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/data')
def data():
    image = cropImage('uploads/'+os.listdir('uploads')[0])
    imageData = readOutlines('static/'+image)

    data = {
        'image': image,
        'width': imageData['width'],
        'height': imageData['height'],
    }
    return jsonify(data)