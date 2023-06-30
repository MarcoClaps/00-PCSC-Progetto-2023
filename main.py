import json
import os
from datetime import datetime

from flask import Flask, request, redirect, url_for
from google.cloud import storage
from werkzeug.utils import secure_filename

# requires pyopenssl

app = Flask(__name__)


# doorbell
@app.route('/', methods=['GET'])
def main():
    return redirect(url_for('static', filename='index.html'))


@app.route('/upload_data_buffer', methods=['POST'])
def upload_data_buffer():
    # print(request.form)
    print(json.loads(request.values['data']))
    return 'saved'


@app.route('/upload_data', methods=['POST'])
def upload_data():
    i = request.form.get("i")
    j = request.form.get("j")
    k = request.form.get("k")
    print(i, j, k)

    return 'saved'


@app.route('/upload', methods=['POST'])
def upload():
    # check if the post request has the file part

    file = request.files['file']

    now = datetime.now()
    current_time = now.strftime("%H_%M_%S")
    fname = f'{current_time}.png'
    # file.save(os.path.join(f'tmp/test_{current_time}.png'))
    client = storage.Client.from_service_account_json("credentials.json")
    bucket = client.bucket('doorbell-db')
    source_file_name = fname
    destination_blob_name = source_file_name
    blob = bucket.blob(destination_blob_name)

    # blob.upload_from_filename(os.path.join('tmp/',fname))

    blob.upload_from_string(file.read(), content_type=file.content_type)
    return 'saved'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
#     , ssl_context='adhoc' canceellato perche non funzionava
