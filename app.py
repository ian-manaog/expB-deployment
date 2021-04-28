import numpy as np
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from starlette.responses import HTMLResponse 
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
import re
import os

from helpers.preprocessor import Preprocessor
from helpers.project import Project

os.environ["CUDA_VISIBLE_DEVICES"]="-1"

app = FastAPI()

class Data(BaseModel):
    text: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], #change this later on for better security
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)



#initialize project resources
project = Project()
project.bootstrap()
project.hash_resources()

#initialize preprocessor class
preprocessor = Preprocessor(project, verbose=False) 
preprocessor.activate_all()

data = pd.read_csv('datasets/A.csv')
prep_texts = preprocessor.bulk_preprocess(data['text'].values) #improve this by saving the cleaned data
tokenizer = Tokenizer(num_words=400, split=' ')
tokenizer.fit_on_texts(prep_texts)


def my_pipeline(text): #pipeline
  text_prep = preprocessor.preprocess(text) #clean and preprocess the data
  X = tokenizer.texts_to_sequences(pd.Series(text_prep).values)
  X = pad_sequences(X, maxlen=31)
  return X


@app.get('/') #basic get view
def basic_view():
    return {"WELCOME": "GO TO /docs route, or /post or send post request to /predict "}



@app.get('/predict', response_class=HTMLResponse) #data input by forms
def take_inp():
    return '''<form method="post"> 
    <input type="text" maxlength="28" name="text" value="Text Emotion to be tested"/>  
    <input type="submit"/> 
    </form>'''



@app.post('/predict') #prediction on data
def predict(data: Data): #input is from forms
    clean_text = my_pipeline(data) #cleaning and preprocessing of the texts
    if clean_text.shape[1] != 0:#if cleantext is not empty
        loaded_model = tf.keras.models.load_model('experimentB.hdf5') #loading the saved model
        predictions = loaded_model.predict(clean_text) #making predictions
        sentiment = int(np.argmax(predictions)) #index of maximum prediction
        probability = max(predictions.tolist()[0]) #probability of maximum prediction
        if sentiment==0: #assigning appropriate name to prediction
            t_sentiment = 'negative'
        elif sentiment==1:
            t_sentiment = 'neutral'
        elif sentiment==2:
            t_sentiment='postive'
        
        return { #returning a dictionary as endpoint
            "ACTUALL SENTENCE": text,
            "PREDICTED SENTIMENT": t_sentiment,
            "Probability": probability
        }
    else:
        return { #returning a dictionary as endpoint
            "ACTUALL SENTENCE": text,
            "PREDICTED SENTIMENT": 'neutral',
            "Probability": 100
        }