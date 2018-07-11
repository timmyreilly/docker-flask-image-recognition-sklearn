# USAGE
# Start the server:
#       python run_keras_server.py
# Submit a request via cURL:
#       curl -X POST -F image=@dog.jpg 'http://localhost:5000/predict'
# Submit a a request via Python:
#       python simple_request.py

# import the necessary packages
# from keras.applications import ResNet50
from keras.models import load_model
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from PIL import Image
import numpy as np
import flask
import io
from keras import backend as K
import os
from importlib import reload

import cntk
print(cntk.__version__)
print(cntk.all_devices()) 


# initialize our Flask application and the Keras model
app = flask.Flask(__name__)
model = None
model = load_model('my_model.h5')

def set_keras_backend(backend):
    if K.backend() != backend: 
        os.environ['KERAS_BACKEND'] = backend
        reload(K)
        assert K.backend() == backend
        


def load_model():
    # load the pre-trained Keras model (here we are using a model
    # pre-trained on ImageNet and provided by Keras, but you can
    # substitute in your own networks just as easily)
    global model
    # try: 
    model = load_model('my_model.h5')
    # except Exception as ex:
    #     print(ex) 
    #     print('lolz ya missed... using resnet ****')
    #     model = ResNet50(weights="imagenet")


def prepare_image(image, target):
    # if the image mode is not RGB, convert it
    if image.mode != "RGB":
        image = image.convert("RGB")

    # resize the input image and preprocess it
    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = imagenet_utils.preprocess_input(image)

    # return the processed image
    return image

cato = {0: 'axes', 1: 'boots', 2: 'carabiners', 3: 'crampons', 4: 'gloves', 5: 'hardshell_jackets', 6: 'harnesses', 7: 'helmets', 8: 'insulated_jackets', 9: 'pulleys', 10: 'rope', 11: 'tents'}

@app.route("/predict", methods=["POST"])
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"success": False}

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            # read the image in PIL format
            image = flask.request.files["image"].read()
            image = Image.open(io.BytesIO(image))

            # preprocess the image and prepare it for classification
            image = prepare_image(image, target=(64, 64))

            # classify the input image and then initialize the list
            # of predictions to return to the client
            result = model.predict(image)
            print(preds) 
            prediction = cato[result.argmax()]


            # loop over the results and add them to the list of
            # returned predictions
            # for (imagenetID, label, prob) in results[0]:
            #     r = {"label": label, "probability": float(prob)}
            #     data["predictions"].append(r)

            # indicate that the request was a success
            data["success"] = True

    # return the data dictionary as a JSON response
    return flask.jsonify(prediction)


# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
    print(("* Loading Keras model and Flask starting server..."
           "please wait until server has fully started"))
    set_keras_backend("cntk")
    # load_model()
    app.run(host='0.0.0.0', debug=False)
