from flask import Flask, request, render_template, jsonify
import os
import io
import base64
from PIL import Image
# from model import generate_caption

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
        # text = generate_caption(os.path.join("uploads", file.filename))
        finding = "Finding"
        impress = "Impression"
        tmp = {"image": encoded_image,
               "captions":
               [{
                   "Finding": "Finding",
                "Impression": "Impression",
                "p": 0.78,
                }, {
                   "Finding": "Finding",
                   "Impression": "Impression",
                   "p": 0.8,
               }]}
        # text = ["123", "456", "789"]
        return jsonify(tmp)
    #     return render_template('index.html', encoded_image=encoded_image, text=text)
    # else:
    #     return "Invalid file format. Allowed formats: png, jpg, jpeg, gif, dicom"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
