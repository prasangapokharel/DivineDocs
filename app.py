from flask import Flask, request, send_file, render_template, jsonify
import os
import mysql.connector
from pdf2docx import Converter
from docx2pdf import convert  # Importing docx2pdf for DOCX to PDF conversion

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# MySQL configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'pdf_converter'
}

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pdf_files (filename, file_path) VALUES (%s, %s)", (file.filename, pdf_path))
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            return jsonify({"error": str(err)}), 500

        word_filename = os.path.splitext(file.filename)[0] + '.docx'
        word_path = os.path.join(UPLOAD_FOLDER, word_filename)

        try:
            # Convert PDF to DOCX
            cv = Converter(pdf_path)
            cv.convert(word_path)
            cv.close()
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return jsonify({
            "original_filename": file.filename,
            "pdf_path": pdf_path,
            "word_filename": word_filename,
            "word_path": word_path
        }), 200
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/word-to-pdf')
def word_to_pdf_form():
    return render_template('word_to_pdf.html')

@app.route('/convert-word-to-pdf', methods=['POST'])
def convert_word_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.docx'):
        word_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(word_path)

        pdf_filename = os.path.splitext(file.filename)[0] + '.pdf'
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        
        try:
            # Convert DOCX to PDF using docx2pdf
            convert(word_path, pdf_path)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return jsonify({
            "original_filename": file.filename,
            "word_path": word_path,
            "pdf_filename": pdf_filename,
            "pdf_path": pdf_path
        }), 200
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = request.args.get('file_path')
    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == "__main__":
    app.run(debug=True)
