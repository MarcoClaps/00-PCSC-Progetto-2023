from FaceRecognition import FaceRecognition

frec = FaceRecognition()

frec.set_parameters("Andre Prova.png")
frec.encode_known_faces()
frec.recognize_faces()
