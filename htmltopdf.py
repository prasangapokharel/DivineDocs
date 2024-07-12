import os
import pdfkit
from flask import Blueprint, request, jsonify, render_template, session
from werkzeug.utils import secure_filename

def create_htmltopdf_blueprint(db_config, add_points):
    htmltopdf_bp = Blueprint('htmltopdf', __name__)
    UPLOAD_FOLDER = 'uploads'

    # Path to the wkhtmltopdf executable
    path_to_wkhtmltopdf = "C:\\Users\\godsu\\Desktop\\python\\DivineDocs\\wkhtmltopdf-master\\bin\\wkhtmltopdf.exe"

    # Configuration for pdfkit
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    @htmltopdf_bp.route('/')
    def html_to_pdf_form():
        return render_template('htmltopdf.html')

    @htmltopdf_bp.route('/upload', methods=['GET', 'POST'])
    def upload_html():
        if request.method == 'POST':
            if 'file' not in request.files:
                return jsonify({"error": "No file part"}), 400
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            if file and file.filename.endswith('.html'):
                html_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
                file.save(html_path)
                pdf_filename = os.path.splitext(file.filename)[0] + '.pdf'
                pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
                try:
                    pdfkit.from_file(html_path, pdf_path, configuration=config, options={'page-size': 'A4', 'dpi': 300})
                    add_points(session.get('user_id'))
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
                return jsonify({"original_filename": file.filename, "html_path": html_path, "pdf_filename": pdf_filename, "pdf_path": pdf_path}), 200
            return jsonify({"error": "Invalid file type"}), 400
        return render_template('upload.html')

    return htmltopdf_bp
