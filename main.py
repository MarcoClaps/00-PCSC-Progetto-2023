import json
from datetime import datetime
from io import BytesIO

from flask import Flask, request, redirect, url_for, render_template
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from secret import secret_key

from google.cloud import storage
from google.cloud import firestore

from FaceRecognition import FaceRecognition
from User import User

# requires pyopenssl


app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
login = LoginManager(app)
login.login_view = '/static/login.html'
# initialize face recognition class
frec = FaceRecognition()


# palceholder for real face recognition funtion
def fecerec():
    return "wellcome"


@login.user_loader
def load_user(username):
    db = firestore.Client.from_service_account_json(
        'facerecognition2023-58824e4fb3cc.json')
    user = db.collection('user_db').document(username).get()
    if user.exists:
        return User(username)
    return None


@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('/main'))
    username = request.values['u']
    password = request.values['p']

    db = firestore.Client.from_service_account_json(
        'facerecognition2023-58824e4fb3cc.json')
    user = db.collection('user_db').document(username).get()
    if user.exists and user.to_dict()['password'] == password:
        login_user(User(username))
        next_page = request.values['next']
        if not next_page:
            next_page = '/dashboard'
        return redirect(next_page)
    return redirect('/static/login.html')


# doorbell
@app.route('/', methods=['GET'])
@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('index.html')


@app.route('/dashboard', methods=['GET'])
@login_required
def load_dashboard():
    return redirect(url_for('static', filename='dashboard.html'))


@app.route('/dashboard/gest_perm', methods=['GET'])
@login_required
def gest_perm():
    client = storage.Client.from_service_account_json(
        'facerecognition2023-84f934357826.json')
    bucket = client.bucket('face_db')
    blobs = bucket.list_blobs(prefix="training/")

    files = []
    for blob in blobs:
        if '.' in blob.name:
            files.append(blob.name)
    names = set([file.split('_')[0].split('/')[1] for file in files])

    print(files)

    return render_template('gest_perm_tmp.html', names=names, files=files)


# per ora l'ho fatto così ma possimo valutare di farlo in un altro modo ad esempio come un pop up
@app.route('/dashboard/gest_perm/add_perm', methods=['GET', 'POST'])
@login_required
def add_perm():
    # se il metodo è get allora carico la pagina

    if request.method == 'GET':
        return url_for('static', filename='add_perm.html')
    # se il metodo è post allora salvo i dati nel db su cloud storage
    else:
        client = storage.Client.from_service_account_json(
            'facerecognition2023-84f934357826.json')
        bucket_name = 'face_db'
        directory_name = 'training/'
        # nel text dovrà essere presente l'id univoco che rappresenta ogni persona
        # TODO: aggiungere un controllo per verificare che l'id sia univoco e che non sia già presente nel db
        text = request.form['text']
        files = request.files.getlist('image')
        print(text, files)

        if text and files:
            bucket = client.bucket(bucket_name)
            for file in files:
                if file:
                    blob = bucket.blob(
                        directory_name + text + '_' + file.filename)
                    blob.upload_from_string(
                        file.read(),
                        content_type=file.content_type
                    )
            return 'Data uploaded successfully'
        else:
            return 'No data selected'


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
        # get the current time
        now = datetime.now()
        print("Accesso alle: ", now)
        # formatto i nomi delle immagini come anno_mese_giorno__ora_minuti_secondi.png
        # Option 1 - Server side
        current_time = now.strftime("%Y_%m_%d__%H_%M_%S")
        fname = f'{current_time}.png'

        # Save the acces photo to the cloud
        client = storage.Client.from_service_account_json(
            'facerecognition2023-84f934357826.json')
        bucket = client.bucket('door_bell')
        source_file_name = fname
        destination_blob_name = source_file_name
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_string(file.read(), content_type=file.content_type)

        # Face recognition
        frec.set_parameters(fname)
        # encode only if necessary
        frec.check_backup_encoded()
        # recognition_results should have only one element
        recognition_result = frec.recognize_faces()

        # first delete the image from the bucket of the doorbell
        blob.delete()
        # then save the image in the bucket of the doorbell
        # source_file_name = fname
        source_file_name = fname.split(".")[0] + '<->' + recognition_result[0]
        destination_blob_name = source_file_name
        blob = bucket.blob(destination_blob_name)
        result_file = recognition_result[1]
        bs = BytesIO()
        result_file.save(bs, 'png')
        # Sarebbe meglio usare l'immagine con il volto messo nel riquadro e il nome

        blob.upload_from_string(bs.getvalue(), content_type="image/png")

        if recognition_result == 'Sconosciuto':
            return 'Utente non riconosciuto'
        else:
            return 'Benvenuto ' + recognition_result[0].split('.p')[0]


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
#     , ssl_context='adhoc' canceellato perche non funzionava
