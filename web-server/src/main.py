import os

import base64
from PIL import Image
from io import BytesIO

import boto3

import numpy as np
import tensorflow as tf

from fastapi import FastAPI, UploadFile, Request
from fastapi.staticfiles import StaticFiles

ACCESS_KEY     = os.environ["ACCESS_KEY"]
SECRET_KEY     = os.environ["SECRET_KEY"]
ENDPOINT_URL   = os.environ["ENDPOINT_URL"]
BUCKET         = os.environ["BUCKET"]
FILENAME       = os.environ["FILENAME"]

LABELS_NAMES = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

app = FastAPI()

def init():
  
  tmp_file="./model/"+FILENAME

  s3 = boto3.client(
      service_name='s3',
      region_name='ru-central1',
      aws_access_key_id=ACCESS_KEY,
      aws_secret_access_key=SECRET_KEY,
      endpoint_url=ENDPOINT_URL
  )
  with open(tmp_file, 'wb') as data:
    s3.download_fileobj(
      Bucket=BUCKET,
      Key=FILENAME,
      Fileobj=data
    )

  return tf.keras.models.load_model(tmp_file)


model = init()


def im_2_b64(image):
    buff = BytesIO()
    image.save(buff, format="JPEG")
    img_str = base64.b64encode(buff.getvalue())
    return img_str

@app.post("/upload")
def create_upload_file(request: Request, file: UploadFile):

    if not file.filename:
      return {"Error": "File is not selected. Please select a file!"}

    image = Image.open(file.file).resize((32, 32), Image.NEAREST).convert("RGB") 

    image_arr = tf.keras.preprocessing.image.img_to_array(image)

    input_arr = np.array([
      image_arr
    ])
    prediction = model.predict(input_arr)

    result=dict(
      map(
        lambda x: (
          x[0],
          str(x[1])
        ),
        sorted(
          zip(
            LABELS_NAMES,
            prediction[0]
          ),
          key=lambda x: x[1],
          reverse=True
        )
      )
    )

    return {
      "image": im_2_b64(image),
      "prediction": result
    }

@app.get("/model")
def get_model():
    #model.summary()
    return {"model": model.to_json() }

app.mount("/", StaticFiles(directory="static", html=True), name="static")