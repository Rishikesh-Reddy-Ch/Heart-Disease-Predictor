import json
import re
import pymongo
import pandas as pd
import pickle as pkl
import numpy as np
from email_validator import validate_email
from sklearn.ensemble import  GradientBoostingClassifier
from datetime import datetime
from geopy.geocoders import Nominatim


database_connection_string="mongodb+srv://heart_health-G64:heart_health-G64@cluster0.2tz5hzd.mongodb.net/"
name_values={'HighBloodPressure':{1:"Yes",3:"No",4:"Borderline high/Pre-hypertensive"},'HadHeartAttack':{1:"Yes",2:"No"},
             'AnyHeartStroke':{1:"Yes",2:"No"},'KidneyDisease':{1:"Yes",2:"No",999:"Don't Know"},
             'Diabetes':{1:"Yes",3:"No",4:"Pre Diabetes",999:"Don't Know"},
             'smoking':{1:"Yes",2:"Some times",3:"Former Smoker",4:"Not Smoker"},
             'exercise':{1:"Yes",2:"No"},'HighCholLevel':{1:"Yes",2:"No"},
             'Gender':{1:"Male",2:"Female"},'Drinker':{1:"Yes",2:"No"}}



def user_idCheck(Username):
    try:
        client=pymongo.MongoClient(database_connection_string)
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
# def numCheck(num):
#     if not re.search(r"[6-9]\d{9}$",num):
#         return False
#     return True
def pinCodeFind(address):
    pin_code=re.findall(r"\d{6}",address)
    if len(pin_code)==1:
        return pin_code[0]
    return False
def addressCheck(address):
    pin_code=pinCodeFind(address=address)
    if pin_code:
        print(pin_code)
        geolocator=Nominatim(user_agent="address_validator")
        try:
            location=geolocator.geocode({"postalcode":pin_code})
            if location:
                return True
        except:
            return False
    return False


def verify_credentials(username, password):
    try:
        client=pymongo.MongoClient(database_connection_string)
        db=client["Heart-health-dataBase"]
        coll=db["Users"]
        user=coll.find({'Username':username,'password':password})
        if list(user):
            return True
        return False
    except:
        return False

def updateCredentials(user):
    try:
        client=pymongo.MongoClient(database_connection_string)
        db=client["Heart-health-dataBase"]
        coll=db["Users"]
        user={
                "Username":user["Username"],
                "password":user["password"],
                "date-of-birth":user["dob"],
                "email":user["email"],
                'address':user['address'],
                'pin-code':pinCodeFind(user["address"]),
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

def age_cal(username):
    client=pymongo.MongoClient(database_connection_string)
    db=client["Heart-health-dataBase"]
    coll=db["Users"]
    user=coll.find_one({"Username":username})

    dob=user["date-of-birth"]
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
        client = pymongo.MongoClient('mongodb+srv://heart_health-G64:heart_health-G64@cluster0.2tz5hzd.mongodb.net/')
        db = client['Heart-health-dataBase']
        cl=db['Users']
        user_cal={"Username":user}
        if data['DiabetesAge']==999:
            data["DiabetesAge"]="dont know"
        # print(user_cal)
        for name in name_values:
            data[name]=name_values[name][data[name]]
        # print(data)
        cl.update_one(user_cal,{"$set":{"record":data}})
        return True
    except:
        return False

def process_data(form_data,names,user):
    try:
        
        form_data['Age Cat'],form_data['Age'] = age_cal(user)
        # del form_data['DateOfBirth']
        form_data['DiabetesAge']=dia_age_cal(form_data['DiabetesAge'])
        for i in names:
            if i not in ['Weight','DateOfBirth']:
                form_data[i]=int(form_data[i])
                # print(int(form_data[i]))
        form_data["Weight"]=float(form_data["Weight"])
        # print("Upto here is Fine!")
        form_data['bmi'] = BMI_cat(form_data['Height'],form_data['Weight'])
        predictionVal,predicted=prediction(form_data,user)
        # print("fine")
        # print(form_data)
        if record(form_data,user) and predicted:
            # print(predictionVal[0])
            return True,prediction_cat(predictionVal[0],user)
        return False,np.NaN
    except:
        return False,np.NaN
def prediction(formData,username):
    try:
        with open("HeartHealth_classifier_model.pkl","rb") as f:
            model=pkl.load(f)
        names=['HighBloodPressure','HadHeartAttack','AnyHeartStroke','KidneyDisease','Diabetes','DiabetesAge','smoking','exercise','HighCholLevel','Gender','Age Cat','bmi','Drinker']
        record=[]
        for i in names:
            record.append(int(formData[i]))
        record=np.array(record).reshape((1,-1))
        # print(record,"fine")
        predictionval=model.predict_proba(record)[:,1]
        # print(prediction)
        return predictionval,True
    except:
        return np.NaN,False
def prediction_cat(value,username):
    if value==np.NaN:
        cat= ""
    elif value<0.047638726968383435:
        cat= 'Low'
    elif value<0.19207434261195536:
        cat= 'Medium'
    else:
        cat='High'
    client=pymongo.MongoClient(database_connection_string)
    db=client["Heart-health-dataBase"]
    coll=db["Users"]
    user=coll.find_one({"Username":username})
    coll.update_one(user,{"$set":{"prediction":value}})
    coll.update_one(user,{"$set":{"prediction-category":cat}})
    return cat
    

def dob_validate(dob):
    year,month,day=map(int,dob.split('-'))
    today=datetime.today()
    if year>today.year:
        return False
    if month>today.month:
        return False
    if day>today.day:
        return False
    return True
