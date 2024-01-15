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
import warnings
import bcrypt
from cryptography.fernet import Fernet
import google.generativeai as genai

with open('key.bin','rb') as Fkey:
    key=Fkey.read()
f=Fernet(key)
warnings.filterwarnings('ignore')
database_connection_string="mongodb+srv://heart_health-G64:heart_health-G64@cluster0.2tz5hzd.mongodb.net/"
name_values={'HighBloodPressure':{1:"Yes",3:"No",4:"Borderline high/Pre-hypertensive"},'KidneyDisease':{1:"Yes",2:"No",999:"Don't Know"},
             'Diabetes':{1:"Yes",3:"No",4:"Pre Diabetes",999:"Don't Know"},
             'smoking':{1:"Yes",2:"Some times",3:"Former Smoker",4:"Not Smoker"},
             'exercise':{1:"Yes",2:"No"},'HighCholLevel':{1:"Yes",2:"No"}, 'Drinker':{1:"Yes",2:"No"},}



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
def pinCodeFind(address):
    pin_code=re.findall(r"\d{6}",address)
    if len(pin_code)==1:
        return pin_code[0]
    return False
def addressCheck(address):
    pin_code=pinCodeFind(address=address)
    if pin_code:
        geolocator=Nominatim(user_agent="address_validator")
        try:
            location=geolocator.geocode({"postalcode":pin_code})
            if location:
                return True
        except :
            return False
    return False


def verify_credentials(username, password):
    try:
        client=pymongo.MongoClient(database_connection_string)
        db=client["Heart-health-dataBase"]
        coll=db["Users"]
        user=coll.find({'Username':username})
        user_list = list(user)

        if user_list:
            if bcrypt.checkpw(password.encode('utf-8'),user_list[0]["password"]):
                return True
        return False
    except:
        return False

def updateCredentials(user):
    try:
        new_password=bcrypt.hashpw(user["password"].encode("utf-8"),bcrypt.gensalt(11))
        client=pymongo.MongoClient(database_connection_string)
        db=client["Heart-health-dataBase"]
        coll=db["Users"]
        user={
                "Username":user["Username"],
                "password":new_password,
                "date-of-birth":f.encrypt(user["dob"].encode('utf-8')),
                "email":f.encrypt(user["email"].encode('utf-8')),
                'Gender':f.encrypt(user['gender'].encode('utf-8'))
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

def age_cal_gender(username):
    client=pymongo.MongoClient(database_connection_string)
    db=client["Heart-health-dataBase"]
    coll=db["Users"]
    user=coll.find_one({"Username":username})

    dob=f.decrypt(user["date-of-birth"]).decode('utf-8')
    gender=f.decrypt(user['Gender']).decode('utf-8')
    if gender=='Male':
        gender=1
    else:
        gender=2
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
    
    return age_cat,age,gender

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
        cl.update_one(user_cal,{"$set":{"record":data}})
        return True,data
    except:
        return False,{}

def process_data(form_data,names,user):
        
        form_data['Age Cat'],form_data['Age'],form_data['Gender'] = age_cal_gender(user)
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
        recorded,Record=record(form_data,user)
        if recorded and predicted:
            # print(predictionVal[0])
            return True,prediction_cat(predictionVal[0],user),Record
        return False,np.NaN,Record    
def prediction(formData,username):
    try:
        with open("HeartHealth_classifier_model.pkl","rb") as f:
            model=pkl.load(f)
        names=['HighBloodPressure','KidneyDisease','Diabetes','DiabetesAge','smoking','exercise','HighCholLevel','Gender','Age Cat','bmi','Drinker']
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
    elif value<0.06889006444901649:
        cat= 'Low'
    elif value<0.2172120495116925:
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
    # print(dob)
    today=datetime.today()
    # print(today)
    if year>today.year:
        return False
    if month>today.month and year==today.year:
        return False
    if day>today.day and year==today.year and month==today.month:
        return False
    return True

def request_email(user,password):
    try:
        if not passwordCheck(password):
            return False,'Password needs: Uppercase, Lowercase, Digit, Special Char.'
        client=pymongo.MongoClient(database_connection_string)
        db=client["Heart-health-dataBase"]
        coll=db["Users"]
        user=coll.find({"Username":user})
        # print(list(user))
        userinfo=list(user)
        if userinfo:
            # print("Hi")
            return f.decrypt(userinfo[0]["email"]).decode('utf-8'),'Success'
        else:
            return False,'Invalid Username'
    except:
        return False,'Cannot Access Database'
def change_password(password,username):
    try:
        client=pymongo.MongoClient(database_connection_string)
        db=client["Heart-health-dataBase"]
        coll=db["Users"]
        user_cal={"Username":username}
        user=coll.find_one(user_cal)
        
        if user:
            new_password=new_password=bcrypt.hashpw(password.encode("utf-8"),bcrypt.gensalt(11))
            coll.update_one({"Username":username},{'$set':{'password':new_password}})
            # print(password)
            return True,'successful'
        else:
            return False,'Invalid Username'
            
        
    except:
        return False,'Cannot Access Database'

def dieteryResponse(record):
        with open('llm_key.bin','rb') as llmkey:
            key=llmkey.read()
        GOOGLE_API_KEY=f.decrypt(key).decode('utf-8')
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        text='**'
        while(re.search(r"\*\*",text)):
            response=model.generate_content('Create a dietery plan for a patient with following abnormalities:\n '+str(record)+ ',Just give the goals and how to achieve them and also compulsorily give the whole rsponse in the form of a inner HTML part')
            text=response.text
        return True, response.text

