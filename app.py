from flask import Flask, request, send_file, render_template, jsonify, redirect, url_for, flash, session
import os
import io
from jpgtopdf import create_jpgtopdf_blueprint
from flask import Response
import mysql.connector
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename
from pdf2docx import Converter
from docx2pdf import convert
from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from texttopdf import create_texttopdf_blueprint
from htmltopdf import create_htmltopdf_blueprint
from webptopdf import create_webptopdf_blueprint
from withdraw import create_withdraw_blueprint

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key
UPLOAD_FOLDER = 'uploads'
PROFILE_PIC_FOLDER = os.path.join(UPLOAD_FOLDER, 'profile_pics')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROFILE_PIC_FOLDER):
    os.makedirs(PROFILE_PIC_FOLDER)

# MySQL configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'pdf_converter'
}

@app.route('/')
def home():
    return render_template('home.html')

def add_points(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET points = points + 1 WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'danger')

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
                cursor.execute("INSERT INTO pdf_files (filename, file_path, user_id) VALUES (%s, %s, %s)", (file.filename, pdf_path, session.get('user_id')))
                conn.commit()
                cursor.close()
                conn.close()
                add_points(session.get('user_id'))
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
            add_points(session.get('user_id'))
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
            add_points(session.get('user_id'))
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
            add_points(session.get('user_id'))
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
            add_points(session.get('user_id'))
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
            user_id = cursor.lastrowid
            cursor.close()
            conn.close()

            # Set session variables
            session['user_id'] = user_id
            session['user_name'] = name
            session['user_email'] = email

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
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                session['user_email'] = email
                flash('Logged in successfully!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password', 'danger')
                return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        flash('You need to login first.', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # Optionally, delete associated user data first
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        session.clear()
        flash('Your account has been successfully deleted.', 'success')
    except mysql.connector.Error as err:
        flash(f"Database Error: {err}", 'danger')
        return redirect(url_for('profile'))
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('home'))


@app.route('/profile_pic')
def profile_pic():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view the profile image.", "danger")
        return redirect(url_for('login'))

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT profile_pic_blob FROM users WHERE id = %s", (user_id,))
        pic_blob = cursor.fetchone()
        if pic_blob:
            return Response(pic_blob[0], mimetype='image/jpeg')
        flash("No profile image found.", "info")
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('profile'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access your profile.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        github = request.form.get('github')
        twitter = request.form.get('twitter')
        instagram = request.form.get('instagram')
        facebook = request.form.get('facebook')
        profile_pic = request.files.get('profile_pic')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        if profile_pic:
            pic_data = profile_pic.read()
            cursor.execute("UPDATE users SET profile_pic_blob = %s WHERE id = %s", (pic_data, user_id))

        cursor.execute("""
            UPDATE users SET name = %s, email = %s, phone = %s, address = %s, 
            github = %s, twitter = %s, instagram = %s, facebook = %s
            WHERE id = %s
        """, (name, email, phone, address, github, twitter, instagram, facebook, user_id))
        conn.commit()
        cursor.close()
        conn.close()

    return render_template('profile.html', user=get_user_details(user_id))

def get_user_details(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

@app.route('/history')
def history():
    if 'user_id' not in session:
        flash('Please log in to access your history.', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT filename, file_path, upload_time FROM pdf_files WHERE user_id = %s", (user_id,))
        files = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'danger')
        return redirect(url_for('home'))
    return render_template('history.html', files=files)

@app.route('/pdf-to-jpg')
def pdf_to_jpg_form():
    return render_template('pdftojpg.html')

@app.route('/convert-pdf-to-jpg', methods=['POST'])
def convert_pdf_to_jpg():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and file.filename.endswith('.pdf'):
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)
        try:
            images = convert_from_path(pdf_path, dpi=300)  # High resolution
            jpg_paths = []
            for i, image in enumerate(images):
                jpg_filename = f"{os.path.splitext(file.filename)[0]}_{i + 1}.jpg"
                jpg_path = os.path.join(UPLOAD_FOLDER, jpg_filename)
                image.save(jpg_path, 'JPEG')
                jpg_paths.append(jpg_path)
            add_points(session.get('user_id'))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        return jsonify({"original_filename": file.filename, "pdf_path": pdf_path, "jpg_paths": jpg_paths}), 200
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/update_profile', methods=['POST'])
def update_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to update your profile.", "danger")
        return redirect(url_for('login'))

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Update profile picture if provided
        profile_pic = request.files.get('profile_pic')
        if profile_pic:
            pic_data = profile_pic.read()
            cursor.execute("UPDATE users SET profile_pic_blob = %s WHERE id = %s", (pic_data, user_id))

        # Update other fields
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        github = request.form.get('github', '')
        twitter = request.form.get('twitter', '')
        instagram = request.form.get('instagram', '')
        facebook = request.form.get('facebook', '')

        # Construct SQL query for updating user details
        cursor.execute("""
            UPDATE users SET 
            name = %s, email = %s, phone = %s, address = %s, 
            github = %s, twitter = %s, instagram = %s, facebook = %s
            WHERE id = %s
        """, (name, email, phone, address, github, twitter, instagram, facebook, user_id))

        conn.commit()
        flash("Profile updated successfully!", "success")
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('profile'))

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = request.args.get('file_path')
    return send_file(file_path, as_attachment=True, download_name=filename)

# Create and register the blueprints
jpgtopdf_bp = create_jpgtopdf_blueprint(db_config, add_points)
texttopdf_bp = create_texttopdf_blueprint(db_config, add_points)
webptopdf_bp = create_webptopdf_blueprint(db_config, add_points)
withdraw_bp = create_withdraw_blueprint(db_config, add_points)  # Create the withdraw blueprint

app.register_blueprint(jpgtopdf_bp, url_prefix='/jpgtopdf')
app.register_blueprint(texttopdf_bp, url_prefix='/texttopdf')
app.register_blueprint(webptopdf_bp, url_prefix='/webptopdf')
app.register_blueprint(withdraw_bp)  # Register the withdraw blueprint

if __name__ == "__main__":
    app.run(debug=True)