from flask import Flask, render_template, request, flash, send_file, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv
import io


ALLOWED_EXTENSIONS = {'webp', 'png', 'jpg', 'jpeg'}
ALLOWED_WM = {'webp', 'png', 'jpg', 'jpeg', 'txt'}


load_dotenv()
Secret_key = os.getenv("SECRET_KEY")
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", Secret_key)


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


def processImage(file, watermark, font_path):
    try:
        if watermark.filename.endswith('.txt'):
            text = watermark.read().decode('utf-8').strip()
            final = final_image(file, text, font_path, (10, 10))
        else:
            img = Image.open(file)
            final = img.resize((500, 500))
            wm = Image.open(watermark)

            # Ensure both images are in "RGBA" mode
            final = final.convert("RGBA")
            wm = wm.convert("RGBA")

            wm_resize = wm.resize((70, 70))

            # Create a transparency mask based on the alpha channel of the watermark
            mask = wm_resize.split()[3]  # The alpha channel

            # Paste the watermark onto the final image using the mask
            final.paste(wm_resize, (10, 10), mask=mask)

        watermarked_img_stream = io.BytesIO()
        final.save(watermarked_img_stream, format='PNG')  # Save as PNG to preserve transparency
        watermarked_img_stream.seek(0)
        return watermarked_img_stream
    except ValueError as e:
        flash("Error processing image: " + str(e))
        return None


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/img', methods=['POST'])
def image():
    global filename, watermark1
    if request.method == 'POST':
        file = request.files['file']
        watermark = request.files['watermark']
        font_path = 'static/Montserrat-Regular.ttf'
        if file and allowed_file(file.filename):
            if watermark and allowed_file1(watermark.filename):

                watermarked_img_stream = processImage(file, watermark, font_path)

                return send_file(watermarked_img_stream,
                                 attachment_filename='watermarked.jpg',
                                 mimetype='image/jpeg')

        flash("Invalid file or watermark format.", 'danger')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=False)

