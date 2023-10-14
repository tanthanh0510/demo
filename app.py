from flask import Flask, request, render_template, jsonify
import os
import io
import base64
from PIL import Image
# from model import generate_caption
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
            # write file to uploads folder and convert to png
            file.save(os.path.join("uploads", file.filename))
            ds = pydicom.dcmread(os.path.join("uploads", file.filename))
            t = (ds.pixel_array - np.min(ds.pixel_array)) / \
                (np.max(ds.pixel_array) - np.min(ds.pixel_array))
            cv2.imwrite(os.path.join(
                "uploads", file.filename.replace(".dcm", ".png")), t*255)
            image_bytes = io.BytesIO(open(os.path.join(
                "uploads", file.filename.replace(".dcm", ".png")), 'rb').read())
            imageName = os.path.join(
                "uploads", file.filename.replace(".dcm", ".png"))
        else:
            image_bytes = io.BytesIO(file.read())
            image = Image.open(image_bytes)
            image.save(os.path.join("uploads", file.filename))
            imageName = os.path.join(
                "uploads", file.filename.replace(".dcm", ".png"))
        encoded_image = base64.b64encode(
            image_bytes.getvalue()).decode('utf-8')
        captions = generate_caption(imageName)
        tmp = {"image": encoded_image,
               "captions":captions}
        return jsonify(tmp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
