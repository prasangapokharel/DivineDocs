from flask import Flask, request, send_file, render_template, jsonify
from pdf2docx import Converter
import fitz  # PyMuPDF
import os
import mysql.connector

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

@app.route('/compress')
def compress_form():
    return render_template('compress.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        # Save file to UPLOAD_FOLDER
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        # Insert file path into database
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pdf_files (filename, file_path) VALUES (%s, %s)", (file.filename, pdf_path))
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            return jsonify({"error": str(err)}), 500

        # Convert PDF to DOCX
        word_filename = os.path.splitext(file.filename)[0] + '.docx'
        word_path = os.path.join(UPLOAD_FOLDER, word_filename)
        converter = Converter(pdf_path)
        converter.convert(word_path)
        converter.close()

        return jsonify({
            "original_filename": file.filename,
            "pdf_path": pdf_path,
            "word_filename": word_filename,
            "word_path": word_path
        }), 200
    return jsonify({"error": "Invalid file type"}), 400

def compress_pdf(input_pdf_path, output_pdf_path, zoom=0.5):
    """
    Compress a PDF file by reducing the resolution of images.
    
    :param input_pdf_path: Path to the input PDF file
    :param output_pdf_path: Path to the output compressed PDF file
    :param zoom: Zoom factor to reduce the image resolution (default is 0.5)
    """
    document = fitz.open(input_pdf_path)
    
    # Iterate through pages
    for page_num in range(len(document)):
        page = document.load_page(page_num)  # Load the page
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))  # Render the page to an image with reduced resolution
        img = fitz.Pixmap(pix, 0) if pix.alpha else pix  # Handle alpha channel
        
        # Create a new PDF page with the reduced resolution image
        new_doc = fitz.open()
        new_page = new_doc.new_page(width=img.width, height=img.height)
        new_page.insert_image(new_page.rect, pixmap=img)
        
        # Replace the original page with the new compressed page
        document[page_num] = new_page
    
    document.save(output_pdf_path, garbage=4, deflate=True)

@app.route('/compress', methods=['POST'])
def compress_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    compression_ratio = request.form.get('compression_ratio', type=int, default=50)
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        # Save file to UPLOAD_FOLDER
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)

        compressed_pdf_path = os.path.join(UPLOAD_FOLDER, 'compressed_' + file.filename)

        # Compress the PDF using PyMuPDF
        compress_pdf(pdf_path, compressed_pdf_path, zoom=compression_ratio/100)

        return jsonify({
            "original_filename": file.filename,
            "pdf_path": pdf_path,
            "compressed_filename": 'compressed_' + file.filename,
            "compressed_pdf_path": compressed_pdf_path
        }), 200
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = request.args.get('file_path')
    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == "__main__":
    app.run(debug=True)
