# === Flask backend for PDF signer web app ===

from flask import Flask, request, send_file, jsonify
import fitz  # PyMuPDF
import os
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
SIGNED_FOLDER = 'signed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SIGNED_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        pdf_file = request.files['pdf']
        sig_file = request.files['signature']
        page = int(request.form['page'])
        x = float(request.form['x'])
        y = float(request.form['y'])

        pdf_filename = secure_filename(pdf_file.filename) if pdf_file.filename else None
        sig_filename = secure_filename(sig_file.filename) if sig_file.filename else None

        if not pdf_filename or not sig_filename:
            return jsonify({"error": "PDF or signature filename missing"}), 400

        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        sig_path = os.path.join(UPLOAD_FOLDER, sig_filename)
        output_path = os.path.join(SIGNED_FOLDER, f"signed_{pdf_filename}")

        pdf_file.save(pdf_path)
        sig_file.save(sig_path)

        # Apply signature
        result = sign_pdf(pdf_path, output_path, sig_path, page, x, y)

        if result:
            return send_file(output_path, as_attachment=True)
        else:
            return jsonify({"error": "Failed to sign PDF"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 400


def sign_pdf(input_path, output_path, sig_path, page_number, x, y, width=150, height=50):
    try:
        pdf = fitz.open(input_path)
        page = pdf[page_number]
        rect = fitz.Rect(x, y, x + width, y + height)
        page.insert_image(rect, filename=sig_path)
        pdf.save(output_path)
        pdf.close()
        return True
    except Exception as e:
        print(f"Error signing PDF: {e}")
        return False

from flask import render_template

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
