from flask import Flask, request, send_file, render_template, jsonify, redirect, url_for, flash
import os
import mysql.connector
from pdf2docx import Converter
from docx2pdf import convert
from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
import pytesseract
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key
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

# Configure pytesseract to use the correct executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\godsu\tesseract-ocr-w64-setup-5.4.0.20240606.exe'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
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
                cv = Converter(pdf_path)
                cv.convert(word_path)
                cv.close()
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            return jsonify({"original_filename": file.filename, "pdf_path": pdf_path, "word_filename": word_filename, "word_path": word_path}), 200
        return jsonify({"error": "Invalid file type"}), 400
    return render_template('upload.html')

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
            convert(word_path, pdf_path)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({"original_filename": file.filename, "word_path": word_path, "pdf_filename": pdf_filename, "pdf_path": pdf_path}), 200
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
            reader = PdfReader(pdf_path)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(password)
            with open(protected_pdf_path, 'wb') as f:
                writer.write(f)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({"original_filename": file.filename, "pdf_path": pdf_path, "protected_filename": protected_pdf_filename, "protected_pdf_path": protected_pdf_path}), 200
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
            reader = PdfReader(pdf_path)
            text_data = ""
            for page in reader.pages:
                text_data += page.extract_text()
            lines = text_data.split("\n")
            data = [line.split() for line in lines if line.strip()]
            df = pd.DataFrame(data)
            df.to_excel(excel_path, index=False)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({"original_filename": file.filename, "pdf_path": pdf_path, "excel_filename": excel_filename, "excel_path": excel_path}), 200
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/merge-pdf')
def merge_pdf_form():
    return render_template('mergepdf.html')

@app.route('/merge-pdf', methods=['POST'])
def merge_pdf():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({"error": "Please upload two PDF files"}), 400
    file1 = request.files['file1']
    file2 = request.files['file2']
    if file1.filename == '' or file2.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file1 and file1.filename.endswith('.pdf') and file2 and file2.filename.endswith('.pdf'):
        pdf_path1 = os.path.join(UPLOAD_FOLDER, file1.filename)
        pdf_path2 = os.path.join(UPLOAD_FOLDER, file2.filename)
        file1.save(pdf_path1)
        file2.save(pdf_path2)
        merged_filename = 'merged_' + file1.filename.split('.')[0] + '_' + file2.filename.split('.')[0] + '.pdf'
        merged_pdf_path = os.path.join(UPLOAD_FOLDER, merged_filename)
        try:
            writer = PdfWriter()
            for path in [pdf_path1, pdf_path2]:
                reader = PdfReader(path)
                for page in reader.pages:
                    writer.add_page(page)
            with open(merged_pdf_path, 'wb') as f:
                writer.write(f)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({"merged_filename": merged_filename, "merged_pdf_path": merged_pdf_path}), 200
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Account created successfully!', 'success')
            return redirect(url_for('home'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and check_password_hash(user[3], password):
                flash('Logged in successfully!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password', 'danger')
                return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/ocr')
def ocr_form():
    return render_template('ocr.html')

@app.route('/convert-ocr', methods=['POST'])
def convert_ocr():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        image_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(image_path)
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({"original_filename": file.filename, "extracted_text": text}), 200
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = request.args.get('file_path')
    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == "__main__":
    app.run(debug=True)
