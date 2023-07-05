from pathlib import Path
import face_recognition
import pickle
from collections import Counter
from PIL import Image, ImageDraw


class FaceRecognition():
    """
    Face recognition class
    """

    def __init__(self):
        """
            - Initialize the class with the default values
            - Check if the folders exist, if not create them
        """
        
        # super variabiles
        self.DEFAULT_ENCODINGS_PATH = Path("face-recognizer\output")
        self.BOUNDING_BOX_COLOR = (0, 0, 255)  # blue
        self.TEXT_COLOR = (255, 255, 255)  # white

        self.input_image = None
        self.validation_path = None
        self.validation_images = list()
        self.name_encodings = None
        self.model = None

        # check lists
        self.checkListWrite = list()
        self.checkListRead = list()

        Path("face-recognizer/training").mkdir(exist_ok=True)
        Path("face-recognizer/output").mkdir(exist_ok=True)
        Path("face-recognizer/validation").mkdir(exist_ok=True)

    def set_parameters(self, input_image=None):
        self.input_image = input_image
        pass

    def encode_known_faces(self, model: str = "cnn"):
        """
        Encodes the known faces and saves them to a file (pickle)
        Args:
            model (str, optional): _description_. Defaults to "cnn".
            encodings_location (Path, optional): _description_. Defaults to DEFAULT_ENCODINGS_PATH.
        """
        print("Encoding known faces...", '\n')
        names = []
        encodings = []
        encodings_location = self.DEFAULT_ENCODINGS_PATH.joinpath(
            'encodings.pkl')

        # look after all pngs in training folder with glob
        for filepath in Path("face-recognizer/training").rglob("*.png"):
            self.validation_path = filepath.name.split(" .")[0]
            # print the path
            print("Encoding: ", self.validation_path)
            # append the path to the list
            self.validation_images.append(filepath)

            # load the image
            image = face_recognition.load_image_file(filepath)
            # found the patches of the face
            face_locations = face_recognition.face_locations(image,
                                                             model=model)
            # encode the face
            face_encodings = face_recognition.face_encodings(image,
                                                             face_locations)

            for encoding in face_encodings:
                names.append(self.validation_path)
                encodings.append(encoding)

        # save the encodings
        self.name_encodings = {"names": names, "encodings": encodings}
        print(encodings_location)
        with encodings_location.open("wb") as f:
            pickle.dump(self.name_encodings, f)

    # private recognition function
    def _recognize_face(self, unknown_encoding, loaded_encodings):
        boolean_matches = face_recognition.compare_faces(
            loaded_encodings["encodings"], unknown_encoding
        )
        votes = Counter(
            name
            for match, name in zip(boolean_matches, loaded_encodings["names"])
            if match
        )
        if votes:
            return votes.most_common(1)[0][0]

    # private function to draw the squares around the faces

    def _display_face(self, draw, bounding_box, name):
        top, right, bottom, left = bounding_box
        draw.rectangle(((left, top), (right, bottom)),
                       outline=self.BOUNDING_BOX_COLOR)
        text_left, text_top, text_right, text_bottom = draw.textbbox(
            (left, bottom), name
        )
        draw.rectangle(
            ((text_left, text_top), (text_right, text_bottom)),
            fill="blue",
            outline="blue",
        )
        draw.text(
            (text_left, text_top),
            name,
            fill="white",
        )

    def recognize_faces(self,
                        model: str = "cnn"):
        """_summary_

        Args:
            image_location (str): _description_
            model (str, optional): _description_. Defaults to "cnn".
        """

        # set the encodings location
        encodings_location = self.DEFAULT_ENCODINGS_PATH.joinpath(
            'encodings.pkl')
        with encodings_location.open(mode="rb") as f:
            loaded_encodings = pickle.load(f)

        self.input_image = face_recognition.load_image_file(self.input_image)

        # find the faces in the image file
        input_face_locations = face_recognition.face_locations(
            self.input_image, model=model
        )
        # find the encodings of the faces
        input_face_encodings = face_recognition.face_encodings(
            self.input_image, input_face_locations
        )

        # generate the pillow image
        pillow_image = Image.fromarray(self.input_image)
        # create the draw object
        draw = ImageDraw.Draw(pillow_image)

        for bounding_box, unknown_encoding in zip(
                input_face_locations, input_face_encodings):
            name = self._recognize_face(unknown_encoding, loaded_encodings)
            if not name:
                name = "Unknown"
            print(name, bounding_box)
            # set the bounding box and the name
            self._display_face(draw, bounding_box, name)

        # delete the draw object
        del draw
        # show the image
        pillow_image.show()

    def validate(self, model: str = "hog"):
        for filepath in Path("face_recognizer/validation").rglob("*"):
            if filepath.is_file():
                self.recognize_faces(image_location=str(filepath.absolute()),
                                     model=model)

    def backup_images_encoded(self):
        # look at all images in the training folder and put em in a list
        for filepath in Path("face-recognizer/training").rglob("*.png"):
            encode_path = filepath.name.split(" .")[0]
            self.checkListWrite.append(encode_path)
        # export in a txt, but then in the bucked
        with open("face-recognizer/validation.txt", "w") as f:
            for item in self.validation_images:
                f.write("%s\n" % item)

    def check_backup_encoded(self):
        try:
            with open("face-recognizer/validation.txt", "r") as f:
                # put everything in a list
                self.checkListRead = list()
                for line in f:
                    self.checkListRead.append(line)
                # if checkListRead is the same as checkListWrite, then everything is ok
                if self.checkListRead == self.checkListWrite:
                    print("No need to encode again")
                else:
                    print("Need to encode again")
                    self.encode_known_faces()
        except:
            print("Need to encode again")
            self.encode_known_faces()
            self.backup_images_encoded()
