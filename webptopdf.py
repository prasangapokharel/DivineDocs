from flask import Blueprint, request, jsonify, render_template, session
import os
from PIL import Image
import mysql.connector
from werkzeug.utils import secure_filename

def create_webptopdf_blueprint(db_config, add_points):
    webptopdf_bp = Blueprint('webptopdf', __name__)
    UPLOAD_FOLDER = 'uploads'

    @webptopdf_bp.route('/')
    def webp_to_pdf_form():
        return render_template('webptopdf.html')

    @webptopdf_bp.route('/upload', methods=['GET', 'POST'])
    def upload_webp():
        if request.method == 'POST':
            if 'file' not in request.files:
                return jsonify({"error": "No file part"}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            if file and file.filename.endswith('.webp'):
                webp_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
                file.save(webp_path)
                pdf_filename = os.path.splitext(file.filename)[0] + '.pdf'
                pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
                try:
                    image = Image.open(webp_path)
                    pdf_bytes = image.convert('RGB')
                    pdf_bytes.save(pdf_path, "PDF", resolution=100.0, save_all=True)
                    add_points(session.get('user_id'))
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
                return jsonify({"original_filename": file.filename, "webp_path": webp_path, "pdf_filename": pdf_filename, "pdf_path": pdf_path}), 200
            return jsonify({"error": "Invalid file type"}), 400
        return render_template('upload.html')

    return webptopdf_bp
