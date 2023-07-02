import json
from datetime import datetime

from flask import Flask, request, redirect, url_for, jsonify
from google.cloud import storage
from FaceRecognition import FaceRecognition

# requires pyopenssl

app = Flask(__name__)
# initialize face recognition class
fr = FaceRecognition()

# palceholder for real face recognition funtion
def fecerec():
    return "wellcome"


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
    if request.method == 'POST':
        file = request.files['file']

        now = datetime.now()
        print(now)
        # formatto i nomi delle immagini come anno_mese_giorno__ora_minuti_secondi.png
        current_time = now.strftime("%Y_%m_%d__%H_%M_%S")
        fname = f'{current_time}.png'
        # file.save(os.path.join(f'tmp/test_{current_time}.png')) non serve passare dal locale
        # purtoppo ho dovuto mettere il link assoluto perche non funzionava con il relativo
        # quindi probabilmente sui vostri pc non va
        client = storage.Client.from_service_account_json("C:\\GitHub\\00-PCSC-Progetto-2023\\facerecognition2023"
                                                          "-84f934357826.json")
        bucket = client.bucket('doorbell-db')
        source_file_name = fname
        destination_blob_name = source_file_name
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_string(file.read(), content_type=file.content_type)
        res = fecerec()
        # return jsonify(result=res)
        return res


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
#     , ssl_context='adhoc' canceellato perche non funzionava
