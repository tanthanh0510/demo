from flask import Flask, request, render_template
import os
import io
import base64
from PIL import Image
import numpy as np
import pydicom
import cv2
from model import generate_caption

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file:
        # check if file is dicom, convert to png
        if file.filename.endswith(".dcm"):
            ds = pydicom.dcmread(file)
            t = (ds.pixel_array - np.min(ds.pixel_array))/(np.max(ds.pixel_array) - np.min(ds.pixel_array))
            cv2.imwrite(os.path.join("uploads", file.filename.replace(".dcm",".png")),t*255)
            encoded_image = base64.b64encode(
                t*255).decode('utf-8')
        else:  
            image_bytes = io.BytesIO(file.read())
            image = Image.open(image_bytes)
            image.save(os.path.join("uploads", file.filename))
            encoded_image = base64.b64encode(
                image_bytes.getvalue()).decode('utf-8')
        
        text = generate_caption(os.path.join("uploads", file.filename))
        return render_template('index.html', encoded_image=encoded_image, text=text)
    else:
        return "Invalid file format. Allowed formats: png, jpg, jpeg, gif, dicom"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
