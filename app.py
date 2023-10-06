from flask import Flask, request, render_template
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
        # Convert image to bytes
        image_bytes = io.BytesIO(file.read())

        # Open image using skimage and save it in "test.png"
        image = Image.open(image_bytes)
        image.save('test.png')

        # Encode image bytes to base64 for HTML display
        encoded_image = base64.b64encode(
            image_bytes.getvalue()).decode('utf-8')

        return render_template('index.html', encoded_image=encoded_image, text="Image Uploaded!")
    else:
        return "Invalid file format. Allowed formats: png, jpg, jpeg, gif"


if __name__ == '__main__':
    app.run(debug=True)
