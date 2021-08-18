from tempfile import NamedTemporaryFile
from flask import Flask, jsonify, request
from rq.job import NoSuchJobError
from werkzeug.utils import send_from_directory
from jobs import queue
from database import database, gridfs
from converter import convert
from settings import PATH_TO_FILES_UPLOAD


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PATH_TO_FILES_UPLOAD


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/audio/upload/<email>', methods=['POST'])
def audio_upload(email):
    if 'file' in request.files:
        file = request.files['file']
        # Check if this email already requested a video to be converted
        email_audio = database.db.audios.find_one({'email': email})
        if not email_audio:
            # Load file to gridfs
            reference = gridfs.put(file.read())
            # Save file reference associated with email
            database.db.audios.insert_one({'email': email, 'original': reference})
            # Enqueue job to process audio based on email
            job = queue.enqueue(convert(email))
            # Return job id
            return jsonify({'job': job.id})
        else:
            return '', 403
    else:
        return '', 404


@app.route('/job/<job_id>/status', methods=['GET'])
def job_status(job_id):
    try:
        job = queue.fetch_job(job_id)
        if job:
            return jsonify({'job': job.id, 'status': job.get_status(), 'result': job.result})
    except NoSuchJobError:
        pass
    return '', 404


@app.route('/audio/converted/<email>', methods=['GET'])
def audio_converted(email):
    email_audio = database.db.audios.find_one({'email': email})
    if email_audio:
        # Check if email_audio is converted
        converted_reference = email_audio.get('converted', '')
        if converted_reference:
            # Get converted audio from gridfs
            reference = gridfs.get(converted_reference)
            # Write content to file
            with NamedTemporaryFile(dir=app.config['UPLOAD_FOLDER']) as f:
                f.write(reference)
                f.flush()
                # Return converted audio
                return send_from_directory(app.config['UPLOAD_FOLDER'], f.name)
    return '', 404