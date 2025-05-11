import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import base64
from utils.classifier import NudityClassifier

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Initialize the nudity classifier
classifier = NudityClassifier()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify_image():
    try:
        # Check if an image file was uploaded
        if 'image' not in request.files:
            logger.error("No image part in the request")
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        
        # Check if the file is empty
        if file.filename == '':
            logger.error("No file selected")
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if the file has an allowed extension
        if not allowed_file(file.filename):
            logger.error(f"File type not allowed: {file.filename}")
            return jsonify({'error': 'File type not allowed. Please upload an image file (png, jpg, jpeg, gif)'}), 400
        
        # Secure the filename to prevent any security issues
        filename = secure_filename(file.filename)
        
        try:
            # Classify the image
            predictions = classifier.classify_image(file)
            
            # Return the classification results
            return jsonify(predictions)
        except Exception as e:
            logger.exception(f"Error classifying image: {str(e)}")
            return jsonify({'error': f'Error processing image: {str(e)}'}), 500
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
