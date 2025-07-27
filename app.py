from flask import Flask, render_template, request, send_from_directory
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from datetime import datetime
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CERTIFICATE_FOLDER = 'certificates'
TEMPLATE_IMAGE = 'static/certificate_template.jpg'

# Create folders if not present
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CERTIFICATE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    file = request.files['csv_file']
    if not file:
        return "No file uploaded", 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    data = pd.read_csv(filepath)

    for index, row in data.iterrows():
        name = row['name']
        course = row['course']
        date = row.get('date', datetime.now().strftime('%d %B %Y'))

        output_path = os.path.join(CERTIFICATE_FOLDER, f"{name.replace(' ', '_')}.pdf")
        generate_certificate(name, course, date, output_path)

    files = os.listdir(CERTIFICATE_FOLDER)
    return render_template('index.html', files=files)

def generate_certificate(name, course, date, output_path):
    PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)
    c = canvas.Canvas(output_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    # Background image
    c.drawImage(ImageReader(TEMPLATE_IMAGE), 0, 0, width=PAGE_WIDTH, height=PAGE_HEIGHT)

    # Text placement
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 + 30, name)

    c.setFont("Helvetica", 20)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 10, f"has completed the course: {course}")
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT / 2 - 40, f"Date: {date}")

    c.save()

@app.route('/certificates/<filename>')
def download(filename):
    return send_from_directory(CERTIFICATE_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
