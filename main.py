import json
from datetime import datetime
import os
from abs_path import abs_firestore, abs_cstorage
from flask import Flask, request, redirect, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from secret import secret_key, usersdb

from google.cloud import storage
from google.cloud import firestore

from FaceRecognition import FaceRecognition
from User import User

# requires pyopenssl


app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
login = LoginManager(app)
login.login_view = '/static/geolocation.html'
# initialize face recognition class
frec = FaceRecognition()


# palceholder for real face recognition funtion
def fecerec():
    return "wellcome"


@login.user_loader
def load_user(username):
    if username in usersdb:
        return User(username)
    return None


@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('/main'))
    username = request.values['u']
    password = request.values['p']
    db = firestore.Client.from_service_account_json(
        abs_firestore)
    user = db.collection('utenti').document(username).get()
    if user.exists and user.to_dict()['password'] == password:
        login_user(User(username))
    return redirect('/static/geolocation.html')


# doorbell
@app.route('/', methods=['GET'])
def main():
    return redirect(url_for('static', filename='index.html'))


@app.route('/dashboard', methods=['GET'])
def main_log():
    return redirect(url_for('static', filename='dashboard.html'))


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
    if request.method == 'POST':
        file = request.files['file']

        now = datetime.now()
        print(now)
        # formatto i nomi delle immagini come anno_mese_giorno__ora_minuti_secondi.png
        # Option 1 - Server side
        current_time = now.strftime("%Y_%m_%d__%H_%M_%S")
        fname = f'{current_time}.png'

        # Option 2 - Local side
        # # save fname in root folder
        # file.save(fname)
        # # save fname in face-recognizer/training folder
        # file.save(f'face-recognizer/training/{fname}')
        # frec.set_parameters(fname)
        # frec.encode_known_faces()
        # frec.recognize_faces()

        # purtoppo ho dovuto mettere il link assoluto perche non funzionava con il relativo
        # quindi probabilmente sui vostri pc non va
        client = storage.Client.from_service_account_json(abs_cstorage)
        bucket = client.bucket('dorbell-db')
        source_file_name = fname
        destination_blob_name = source_file_name
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_string(file.read(), content_type=file.content_type)
        res = fecerec()
        # return jsonify(result=res)
        return res


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
#     , ssl_context='adhoc' canceellato perche non funzionava
