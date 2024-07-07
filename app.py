from flask import Flask, request, send_file, render_template, jsonify
import os
import mysql.connector
from pdf2docx import Converter
from docx2pdf import convert  # Importing docx2pdf for DOCX to PDF conversion
from PyPDF2 import PdfReader, PdfWriter  # Importing PdfReader and PdfWriter for PDF protection
import pandas as pd

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

@app.route('/protect-pdf')
def protect_pdf_form():
    return render_template('protectpdf.html')

@app.route('/protect-pdf', methods=['POST'])
def protect_pdf():
    if 'file' not in request.files or 'password' not in request.form:
        return jsonify({"error": "No file part or password"}), 400
    file = request.files['file']
    password = request.form['password']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        protected_pdf_filename = os.path.splitext(file.filename)[0] + '_protected.pdf'
        protected_pdf_path = os.path.join(UPLOAD_FOLDER, protected_pdf_filename)

        try:
            # Protect the PDF with a password
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(password)
            with open(protected_pdf_path, 'wb') as f:
                writer.write(f)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return jsonify({
            "original_filename": file.filename,
            "pdf_path": pdf_path,
            "protected_filename": protected_pdf_filename,
            "protected_pdf_path": protected_pdf_path
        }), 200
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/pdf-to-excel')
def pdf_to_excel_form():
    return render_template('pdf_to_excel.html')

@app.route('/convert-pdf-to-excel', methods=['POST'])
def convert_pdf_to_excel():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        excel_filename = os.path.splitext(file.filename)[0] + '.xlsx'
        excel_path = os.path.join(UPLOAD_FOLDER, excel_filename)

        try:
            # Extract text from PDF
            reader = PdfReader(pdf_path)
            text_data = ""
            for page in reader.pages:
                text_data += page.extract_text()

            # Process text data into a structured format
            # This example assumes the data is space-separated, adjust accordingly
            lines = text_data.split("\n")
            data = [line.split() for line in lines if line.strip()]

            # Create a DataFrame
            df = pd.DataFrame(data)

            # Save DataFrame to Excel
            df.to_excel(excel_path, index=False)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return jsonify({
            "original_filename": file.filename,
            "pdf_path": pdf_path,
            "excel_filename": excel_filename,
            "excel_path": excel_path
        }), 200
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = request.args.get('file_path')
    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == "__main__":
    app.run(debug=True)
