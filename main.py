from flask import Flask, render_template, request, flash, send_file, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv
import io

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'webp', 'png', 'jpg', 'jpeg'}
ALLOWED_WM = {'webp', 'png', 'jpg', 'jpeg', 'txt'}
uploads_folder_path = os.path.join(os.path.dirname(__file__), 'uploads')


app = Flask(__name__)
load_dotenv
Secret_key = os.getenv("SECRET_KEY")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", Secret_key)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///images.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file1(watermark):
    return '.' in watermark and \
           watermark.rsplit('.', 1)[1].lower() in ALLOWED_WM


def final_image(image_path, text, font_path, position):
    img = Image.open(image_path)
    img = img.resize((500, 500))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, 36)
    draw.text(position, text, font=font, fill=(0, 0, 0))
    return img


def processImage(file, watermark):
    if watermark.filename.endswith('.txt'):
        text = watermark.read().decode('utf-8').strip()
        final = final_image(file, text, 'arial.ttf', (10, 10))
    else:
        img = Image.open(file)
        final = img.resize((500, 500))
        wm = Image.open(watermark)
        wm_resize = wm.resize((70, 70))
        final.paste(wm_resize, (10, 10), mask=wm_resize)

    watermarked_img_stream = io.BytesIO()
    final.save(watermarked_img_stream, format='JPEG')
    watermarked_img_stream.seek(0)
    return watermarked_img_stream


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/img', methods=['POST'])
def image():
    global filename, watermark1
    if request.method == 'POST':
        file = request.files['file']
        watermark = request.files['watermark']
        if file and allowed_file(file.filename):
            if watermark and allowed_file1(watermark.filename):

                watermarked_img_stream = processImage(file, watermark)

                return send_file(watermarked_img_stream,
                                 attachment_filename='watermarked.jpg',
                                 mimetype='image/jpeg')
        flash("Invalid file or watermark format.")
        return render_template('index.html')


app.run(debug=True)

