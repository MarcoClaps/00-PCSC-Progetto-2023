from FaceRecognition import FaceRecognition

frec = FaceRecognition()

fname="Prova.png"
frec.set_parameters(fname)
# encode only if necessary
frec.check_backup_encoded()
frec.recognize_faces()
