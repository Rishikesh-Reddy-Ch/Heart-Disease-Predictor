import json
import re
import pymongo
import pandas as pd
import pickle as pkl
import numpy as np
from email_validator import validate_email
from sklearn.ensemble import  GradientBoostingClassifier
from datetime import datetime
def user_idCheck(Username):
    try:
        client=pymongo.MongoClient("mongodb://localhost:27017/")
        db=client["Heart-health-dataBase"]
        coll=db["Users"]
        user=coll.find({'Username':Username})
        if list(user):
            return False
        return True
    except:
        return False
def passwordCheck(password):
    if len(password) < 8:
        return False
    
    if not re.search(r"[A-Z]", password):
        return False
    
    if not re.search(r"[a-z]", password):
        return False
    
    if not re.search(r"\d", password):
        return False
    
    if not re.search(r"\W", password):
        return False
    
    return True
def numCheck(num):
    if not re.search(r"[6-9]\d{9}$",num):
        return False
    return True

def verify_credentials(username, password):
    try:
        client=pymongo.MongoClient("mongodb://localhost:27017/")
        db=client["Heart-health-dataBase"]
        coll=db["Users"]
        user=coll.find({'Username':username,'password':password})
        if list(user):
            return True
        return False
    except:
        return False
def updateCredentials(Username,password,phoneNum,email):
    try:
        client=pymongo.MongoClient("mongodb://localhost:27017/")
        db=client["Heart-health-dataBase"]
        coll=db["Users"]
        user={
                "Username":Username,
                "password":password,
                "phoneNum":phoneNum,
                "email":email,
                "record":{} 
        }
        coll.insert_one(user)
        return True
    except:
        return False

def emailValidate(email):
    try:
        if validate_email(email):
            return True
        return False
    except:
        return False

def age_cal(dob):
    dob='2004-12-07'
    year,month,day = map(int,dob.split('-'))
    # print(year,month,day)
    today = datetime.today()
    # print(type(today))
    if today.month-month > 0:
        age= today.year - year
    elif today.month == month:
        if  today.day < day:
            age = today.year - year - 1
        else:
            age = today.year - year
    else:
        age = today.year - year - 1
    
    if age>=18 and age<=24:
        age_cat = 1
    elif age>=25 and age<=29:
        age_cat = 2
    elif age>=30 and age<=34:
        age_cat =3
    elif age>=35 and age<=39:
        age_cat = 4
    elif age>=40 and age<=44:
        age_cat = 5
    elif age>=45 and age<=49:
        age_cat = 6
    elif age>=50 and age<=54:
        age_cat = 7
    elif age>=55 and age<=59:
        age_cat = 8
    elif age>=60 and age<=64:
        age_cat = 9
    elif age>=65 and age<=69:
        age_cat = 10
    elif age>=70 and age<=74:
        age_cat = 11
    elif age>=75 and age<=79:
        age_cat = 12
    elif age>=80:
        age_cat = 13
    else:
        age_cat = 14
    
    return age_cat,age

def BMI_cat(height,weight):
    height,weight = int(height),int(weight)*100
    bmi = weight/(height**2)
    if(bmi<18.5):
        cat=1 
    elif(bmi>=18.5 and bmi<25):
        cat=2
    elif(bmi>=25 and bmi<30):
        cat = 3
    elif(bmi>=30):
        cat = 4
    return cat

def dia_age_cal(dia_age):
    if dia_age=="":
        return "999"
    return dia_age
    
def record(data,user):
    # print("Hello",user)
    try:
        client = pymongo.MongoClient('mongodb://localhost:27017/')
        db = client['Heart-health-dataBase']
        cl=db['Users']
        user_cal={"Username":"Rishi"}
        # print(user_cal)
        cl.update_one(user_cal,{"$push":{"record":data}})
        return True
    except:
        return False

def process_data(form_data,names,user):
    try:
        form_data['Age Cat'],form_data['Age'] = age_cal(form_data['DateOfBirth'])
        # del form_data['DateOfBirth']
        form_data['DiabetesAge']=dia_age_cal(form_data['DiabetesAge'])
        for i in names:
            if i not in ['Weight','DateOfBirth']:
                form_data[i]=int(form_data[i])
                # print(int(form_data[i]))
        form_data["Weight"]=float(form_data["Weight"])
        # print("Upto here is Fine!")
        form_data['bmi'] = BMI_cat(form_data['Height'],form_data['Weight'])
        prdictionVal,predicted=prediction(form_data)
        print("fine")
        if record(form_data,user) and predicted:
            print(prdictionVal[0])
            return True,prdictionVal[0]
        return False,np.NaN
    except:
        return False,np.NaN
def prediction(formData):
    try:
        with open("HeartHealth_classifier_model.pkl","rb") as f:
            model=pkl.load(f)
        names=['HighBloodPressure','HadHeartAttack','AnyHeartStroke','KidneyDisease','Diabetis','DiabetesAge','smoking','exercise','HighCholLevel','Gender','Age Cat','bmi','Drinker']
        record=[]
        for i in names:
            record.append(int(formData[i]))
        record=np.array(record).reshape((1,-1))
        print(record,"fine")
        return model.predict_proba(record)[:,1],True
    except:
        return np.NaN,False

