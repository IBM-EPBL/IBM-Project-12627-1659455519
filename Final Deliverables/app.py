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
from cloudant.client import Cloudant

model1=load_model('./Model/body.h5')
model2 = load_model('./Model/level.h5')
app=Flask(__name__)
client = Cloudant.iam("c059a4ef-8c13-4d65-bc33-da592b41838a-bluemix", "511lW2p85eY0cZqJRC5srXUULERV69Ru9z9UxM4lwngE", connect=True)
my_database=client.create_database('my_database')
app.secret_key = 'Nothing'

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/index.html/')
def home():
    return render_template('index.html')

@app.route('/register/', methods=["GET","POST"])
def register():
    return render_template('register.html')

@app.route('/afterreg/', methods=["GET","POST"])
def afterreg():
    x=[x for x in request.form.values()]
    print(x)
    data={
        '_id':x[1],
        'name':x[0],
        'psw':x[2]
    }
    print(data)
    query={'_id':{'$eq': data['_id']}}
    docs= my_database.get_query_result(query)
    print(docs)
    print(len(docs.all()))
    if(len(docs.all())==0):
        url=my_database.create_document(data)
        return render_template('register.html', errors="Registration Successful, Please Login")
    else:
        return render_template('register.html', errors="Your Account already exist, Please Login Using that")

@app.route('/login/',methods=["GET","POST"])
def login():
    if('user' in session):
        return render_template('prediction.html')
    else:
        return render_template('login.html')


@app.route('/afterlogin/', methods=["GET", "POST"])
def afterlogin():
    user=request.form['_id']
    passw=request.form['psw']
    print(user,passw)
    query={'_id':{'$eq':user}}
    docs=my_database.get_query_result(query)
    print(docs)
    print(len(docs.all()))
    if(len(docs.all())==0):
        return render_template('login.html', errors="Username not found")
    else:
        if((user==docs[0][0]['_id'] and passw==docs[0][0]['psw'])):
            session['user'] = user
            return redirect(url_for('prediction'))
        else:
            return render_template('login.html', errors="Wrong Credentials.")

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