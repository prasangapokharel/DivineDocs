from flask import Blueprint, request, jsonify, render_template, session
import os
from werkzeug.utils import secure_filename
from PIL import Image
import mysql.connector

def create_jpgtopdf_blueprint(db_config, add_points):
    jpgtopdf_bp = Blueprint('jpgtopdf', __name__)
    UPLOAD_FOLDER = 'uploads'

    @jpgtopdf_bp.route('/')
    def jpg_to_pdf_form():
        return render_template('jpgtopdf.html')

    @jpgtopdf_bp.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            if 'file' not in request.files:
                return jsonify({"error": "No file part"}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            if file and file.filename.endswith('.jpg'):
                jpg_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
                file.save(jpg_path)
                pdf_filename = os.path.splitext(file.filename)[0] + '.pdf'
                pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
                try:
                    image = Image.open(jpg_path)
                    pdf_bytes = image.convert('RGB')
                    pdf_bytes.save(pdf_path)
                    add_points(session.get('user_id'))
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
                return jsonify({"original_filename": file.filename, "jpg_path": jpg_path, "pdf_filename": pdf_filename, "pdf_path": pdf_path}), 200
            return jsonify({"error": "Invalid file type"}), 400
        return render_template('upload.html')

    return jpgtopdf_bp
