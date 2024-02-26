import time
from flask import Flask, request, render_template, jsonify
import os
import io
import base64
from PIL import Image
import numpy as np
import pydicom
import cv2
from model import generate_caption, segment
from documents import default
app = Flask(__name__)

app.register_blueprint(default)

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
        assert file.filename.endswith(".dcm") or file.filename.endswith(
            ".png") or file.filename.endswith(".jpg") or file.filename.endswith(".jpeg"), "File must be in .dcm, .png, .jpg, .jpeg format"
        
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
        start_time = time.time()
        captions = generate_caption(imageName)
        segmented_image = segment(imageName)
        segmented_image_name = os.path.join(
            "uploads", file.filename.replace(".dcm", "_segmented.png"))
        segmented_image.save(segmented_image_name)
        encoded_seg = base64.b64encode(
            open(segmented_image_name, 'rb').read()).decode('utf-8')
        end_time = time.time()
        print("Time taken: {}".format(end_time - start_time))
        tmp = {"image": encoded_image,
                "segmented_image": encoded_seg,
               "captions":captions}
        return jsonify(tmp)

