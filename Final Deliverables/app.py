import re
import numpy as np
import os
from flask import Flask, app,request,render_template,redirect,url_for,session
from tensorflow.keras import models
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.python.ops.gen_array_ops import concat
from tensorflow.keras.applications.inception_v3 import preprocess_input
import requests
import pyrebase

model1=load_model('./Model/body.h5')
model2 = load_model('./Model/level.h5')
app=Flask(__name__)

config = {
    "apiKey": "AIzaSyAb9hsB-xOPtt5wker-s0iw6KsYExi6r0w",
    "authDomain": "vehicle-damage-detection-840aa.firebaseapp.com",
    "projectId": "vehicle-damage-detection-840aa",
    "storageBucket": "vehicle-damage-detection-840aa.appspot.com",
    "messagingSenderId": "33611026551",
    "appId": "1:33611026551:web:db531a9a6623d72fb93672",
    "measurementId": "G-C32ENMFQ1Z",
    "databaseURL": ""
}
firebase = pyrebase.initialize_app(config)
autha = firebase.auth()
app.secret_key = "secret"

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/index.html/')
def home():
    return render_template('index.html')

@app.route('/register/', methods=["GET","POST"])
def register():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        try:
            autha.create_user_with_email_and_password(email,password)
            return render_template('login.html')
        except:
            return render_template('register.html',errors="Something Went Wrong Try Again")
    return render_template('register.html')

@app.route('/login/',methods=["GET","POST"])
def login():
    if('user' in session):
        return render_template('prediction.html')
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user=autha.sign_in_with_email_and_password(email,password)
            session['user']=email
            return render_template('prediction.html')
        except:
            return render_template('login.html', errors="Failed To Login")
    return render_template('login.html')

@app.route('/logout/')
def logout():
    session.pop('user')
    return render_template('logout.html')

@app.route('/prediction/')
def prediction():
    if('user' in session):
        return render_template('prediction.html')
    else:
        return render_template('login.html')

@app.route('/result/',methods=["GET","POST"])
def res():
    if request.method=="POST":
        f=request.files['file']
        basepath=os.path.dirname(__file__)
        filepath=os.path.join(basepath,"hello.jpg")
        f.save(filepath)
        
        img=image.load_img(filepath,target_size=(224,224))
        x=image.img_to_array(img)
        x=np.expand_dims(x,axis=0)
        img_data=preprocess_input(x)
        prediction1=np.argmax(model1.predict(img_data))
        prediction2=np.argmax(model2.predict(img_data))
        index1=['front','rear','side']
        index2=['minor','moderate','severe']
        result1=index1[prediction1]
        result2=index2[prediction2]
        if(result1=="front" and result2=="minor"):
            value="3000 - 5000 INR"
        elif(result1 == "front" and result2 == "moderate"):
            value = "6000 - 8000 INR"
        elif(result1 == "front" and result2 == "severe"):
            value = "9000 - 11000 INR"
        elif(result1 == "rear" and result2 == "minor"):
            value = "4000 - 6000 INR"
        elif(result1 == "rear" and result2 == "moderate"):
            value = "7000 - 9000 INR"
        elif(result1 == "rear" and result2 == "severe"):
            value = "11000 - 13000 INR"
        elif(result1 == "side" and result2 == "minor"):
            value = "6000 - 8000 INR"
        elif(result1 == "side" and result2 == "moderate"):
            value = "9000 - 11000 INR"
        elif(result1 == "side" and result2 == "severe"):
            value = "12000 - 15000 INR"
        else:
            value="16000 - 50000 INR"
        return render_template('prediction.html',prediction=value)


if __name__ == "__main__":
    app.run()