from flask import Flask, request, render_template
import os
import io
import base64
from PIL import Image

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
        image_bytes = io.BytesIO(file.read())
        image = Image.open(image_bytes)
        image.save(os.path.join("uploads", file.filename))
        encoded_image = base64.b64encode(
            image_bytes.getvalue()).decode('utf-8')
        text = "Image Uploaded!\nImage Uploaded1!".split("\n")
        return render_template('index.html', encoded_image=encoded_image, text=text)
    else:
        return "Invalid file format. Allowed formats: png, jpg, jpeg, gif, dicom"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
