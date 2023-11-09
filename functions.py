import json
import re
import pymongo
import pandas as pd
import pickle as pkl
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
    return age

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
        form_data['age'] = age_cal(form_data['DateOfBirth'])
        # del form_data['DateOfBirth']
        form_data['DiabetesAge']=dia_age_cal(form_data['DiabetesAge'])
        for i in names:
            if i not in ['Weight','DateOfBirth']:
                form_data[i]=int(form_data[i])
                # print(int(form_data[i]))
        form_data["Weight"]=float(form_data["Weight"])
        # print("Upto here is Fine!")
        form_data['bmi'] = BMI_cat(form_data['Height'],form_data['Weight'])
        if record(form_data,user):
            return True
        return False
    except:
        return False
# def prediction(formData,user):
#     df=pd.dataframe(formData)
#     print(df)
#     df.to_csv("temp.csv")
#     with open("HeartHealth_classifier_model.pkl","rb") as f:
#         model=pkl.load(f)
#     model.predict_proba

