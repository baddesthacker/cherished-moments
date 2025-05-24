from flask import Flask, render_template, request, redirect, url_for, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Use Windows-safe paths
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file types
ALLOWED_IMAGE = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEO = {'mp4', 'mov', 'avi'}


def allowed_file(filename, file_type='image'):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'image':
        return ext in ALLOWED_IMAGE
    elif file_type == 'video':
        return ext in ALLOWED_VIDEO
    return False


@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()

    if username == 'mybestfriend' and password == '14/9/2001':
        session['logged_in'] = True
        return redirect(url_for('home'))
    else:
        return render_template('login.html', error="Invalid credentials")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('index'))

    saved_items = []

    # Load uploaded files
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], f)
        if os.path.isfile(full_path):
            name, ext = os.path.splitext(f)
            url_path = f"/static/uploads/{f}"
            file_type = 'image' if ext[1:].lower(
            ) in ALLOWED_IMAGE else 'video'
            saved_items.append({
                'type': file_type,
                'content': url_path,
                'name': name,
                'date': os.path.getmtime(full_path)
            })

    if request.method == 'POST':
        image = request.files.get('image')
        video = request.files.get('video')

        if image and allowed_file(image.filename, 'image'):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if video and allowed_file(video.filename, 'video'):
            filename = secure_filename(video.filename)
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return redirect(url_for('home'))

    return render_template('home.html', saved_items=saved_items)


if __name__ == '__main__':
    # Use_reloader=False recommended for Windows
    app.run(host='0.0.0.0', port=5000, debug=True)
