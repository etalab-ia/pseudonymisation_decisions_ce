import os
import tempfile
from api.app import app
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from api.data_loader import sent_tokenizer, word_tokenizer, tagger
import run.process_file as pf

ALLOWED_EXTENSIONS = set(['doc', 'docx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(tempfile.gettempdir(), filename))
            pf.process_file(os.path.join(tempfile.gettempdir(), filename),
                            os.path.join(app.config['UPLOAD_FOLDER'], filename),
                            sent_tokenizer,
                            word_tokenizer,
                            tagger)

            flash('File successfully uploaded')
            return redirect('/')
        else:
            flash("Allowed file types are 'doc' and 'docx'")
            return redirect(request.url)


if __name__ == "__main__":
    app.run()