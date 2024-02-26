import time
from datetime import datetime
from flask import Flask, request, render_template, jsonify
import os
import io
from PIL import Image
import numpy as np
import pydicom
import cv2
from model import generate_caption, segment
from documents import default
from utils import uploadFile

app = Flask(__name__)

if not os.path.exists("Uploads"):
    os.makedirs("Uploads/Images")
    os.makedirs("Uploads/Segment")
    os.makedirs("Uploads/Dataset/files")
    os.makedirs("Uploads/Dataset/captions")

app.register_blueprint(default)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"code": 0, "message": "No file part"})

        file = request.files['file']

        if file.filename == '':
            return jsonify({"code": 0, "message": "No selected file"})

        if file:
            # check if file is dicom, convert to png
            assert file.filename.endswith(".dcm") or file.filename.endswith(
                ".png") or file.filename.endswith(".jpg") or file.filename.endswith(".jpeg"), "File must be in .dcm, .png, .jpg, .jpeg format"
            
            if file.filename.endswith(".dcm"):
                # write file to uploads folder and convert to png
                file.save(os.path.join("Uploads/Images", file.filename))
                ds = pydicom.dcmread(os.path.join("Uploads/Images", file.filename))
                t = (ds.pixel_array - np.min(ds.pixel_array)) / \
                    (np.max(ds.pixel_array) - np.min(ds.pixel_array))            
                imageName = os.path.join(
                    "Uploads/Images", file.filename.replace(".dcm", ".png"))
                cv2.imwrite(imageName, t*255)
            else:
                image_bytes = io.BytesIO(file.read())
                image = Image.open(image_bytes)
                imageName = os.path.join(
                    "Uploads/Images", file.filename)
                image.save(imageName)
            start_time = time.time()
            captions = generate_caption(imageName)
            segmented_image = segment(imageName)
            image_url = uploadFile(imageName)
            segmented_image_name = imageName.replace("Images", "Segment")
            segmented_image.save(segmented_image_name)
            image_seg_url = uploadFile(segmented_image_name)
            end_time = time.time()
            # remove imageName and segmented_image_name
            os.remove(imageName)
            os.remove(segmented_image_name)
            print("Time taken: {}".format(end_time - start_time))
            data = {"image": image_url,
                    "segmented_image": image_seg_url,
                "captions":captions}
            output = {
                "code": 1,
                "data": data,
            }
            return jsonify(output)
        else:
            return jsonify({"code": 0, "message": "Upload failed"})
    except Exception as e:
        return jsonify({"code": 0, "message": str(e)})


@app.route('/update', methods=['POST'])
def update_caption():
    try:
        if 'file' not in request.files:
            return jsonify({"code": 0, "message": "No file part"})

        file = request.files['file']
        caption = request.form['caption']
        if file.filename == '':
            return jsonify({"code": 0, "message": "No selected file"})

        if caption == '':
            return jsonify({"code": 0, "message": "No caption"})
        # create name is current time + file name
        file_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") +"-"+ file.filename
        file_name_path = os.path.join("Uploads/Dataset/files", file_name)
        caption_file = os.path.join("Uploads/Dataset/captions", file_name.replace(".png", ".txt"))
        file.save(file_name_path)
        with open(caption_file, "w") as f:
            f.write(caption)

        if uploadFile(file_name_path) and uploadFile(caption_file):
            os.remove(file_name_path)
            os.remove(caption_file)
            return jsonify({"code": 1, "message": "Upload successful"})
        
        return jsonify({"code": 0, "message": "Upload failed"})
    except Exception as e:
        return jsonify({"code": 0, "message": str(e)})
    