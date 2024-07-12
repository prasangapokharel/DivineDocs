from flask import Blueprint, request, jsonify, render_template, session
import os
from fpdf import FPDF
import mysql.connector
from werkzeug.utils import secure_filename

def create_texttopdf_blueprint(db_config, add_points):
    texttopdf_bp = Blueprint('texttopdf', __name__)
    UPLOAD_FOLDER = 'uploads'

    @texttopdf_bp.route('/')
    def text_to_pdf_form():
        return render_template('texttopdf.html')

    @texttopdf_bp.route('/upload', methods=['GET', 'POST'])
    def upload_text():
        if request.method == 'POST':
            if 'file' not in request.files:
                return jsonify({"error": "No file part"}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            if file and file.filename.endswith('.txt'):
                text_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
                file.save(text_path)
                pdf_filename = os.path.splitext(file.filename)[0] + '.pdf'
                pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.set_font("Arial", size=12)
                    with open(text_path, 'r') as f:
                        for line in f:
                            pdf.multi_cell(0, 10, line)
                    pdf.output(pdf_path)
                    add_points(session.get('user_id'))
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
                return jsonify({"original_filename": file.filename, "text_path": text_path, "pdf_filename": pdf_filename, "pdf_path": pdf_path}), 200
            return jsonify({"error": "Invalid file type"}), 400
        return render_template('upload.html')

    return texttopdf_bp
