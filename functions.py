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
import bcrypt
from cryptography.fernet import Fernet
import google.generativeai as genai
from openai import OpenAI
import os

# Load Fernet key from environment variable FERNET_KEY (preferred) or fallback to key.bin
fernet_key = None
if os.environ.get('FERNET_KEY'):
    # Stored in .env as text
    fernet_key = os.environ.get('FERNET_KEY').encode('utf-8')
else:
    try:
        with open('key.bin','rb') as Fkey:
            fernet_key = Fkey.read()
    except Exception:
        fernet_key = None

if not fernet_key:
    raise RuntimeError('FERNET key not found in environment or key.bin')

f = Fernet(fernet_key)

# Load encrypted LLM key (LLM_KEY_ENC) from environment or fallback to llm_key.bin
llm_key_enc = None
if os.environ.get('LLM_KEY_ENC'):
    llm_key_enc = os.environ.get('LLM_KEY_ENC').encode('utf-8')
else:
    try:
        with open('llm_key.bin','rb') as llmkey:
            llm_key_enc = llmkey.read()
    except Exception:
        llm_key_enc = None

if not llm_key_enc:
    raise RuntimeError('Encrypted LLM key not found in environment or llm_key.bin')

client = OpenAI(api_key=f.decrypt(llm_key_enc).decode('utf-8'))

database_connection_string="mongodb+srv://heart_health-G64:heart_health-G64@cluster0.2tz5hzd.mongodb.net/"

async def user_idCheck(Username):
    try:
        client=pymongo.MongoClient(database_connection_string)
        db=client["Heart-health-dataBase"]
        coll=db["Users"]
        user=coll.find({'Username':Username})
        if list(user):
            return False,""
        return True,""
    except:
        return False,"UnableToAccessDatabase"
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
async def addressCheck(address):
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


async def verify_credentials(username, password):
    try:
        client=pymongo.MongoClient(database_connection_string)
        db=client["Heart-health-dataBase"]
        coll=db["Users"]
        user=coll.find_one({'Username':username})
        user_list = dict(user)

        if user_list:
            if bcrypt.checkpw(password.encode('utf-8'),user_list["password"]):
                return True,''
        return False,''
    except:
        return False,"Unable to access database"

async def updateCredentials(user):
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
        return False,'Cannot access database'

def emailValidate(email):
    try:
        if validate_email(email,check_deliverability=True):
            return True
        return False
    except:
        return False

async def age_cal_gender(username,iscat):
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
    if iscat:
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
    return age,gender
def BMI_cat(height,weight):
    height,weight = int(height)/100,int(weight)
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

# def dia_age_cal(dia_age):
#     if dia_age=="":
#         return "999"
#     return dia_age
    
async def record(data,user):
    # print("Hello",user)
    try:
        record={}
        record.update(data)
        client = pymongo.MongoClient('mongodb+srv://heart_health-G64:heart_health-G64@cluster0.2tz5hzd.mongodb.net/')
        db = client['Heart-health-dataBase']
        cl=db['Users']
        user_cal={"Username":user}
        
        # print(user_cal)
        with open('name_values.json','r') as fp:
            name_values=json.load(fp)[1]
        for name in data:
            if name not in name_values:
                record[name]=int(data[name])
            else:
                record[name]=name_values[name][record[name]] 
        if record['DiabetesAge']==999:
            record["DiabetesAge"]="dont know"
        del record['Gender'],record['bmi'],record['HighBloodPressure'],record['HighCholLevel'],record['Age Cat'],  
        cl.update_one(user_cal,{"$set":{"record":record}})
        return True,record
    except:
        return False,{}
def BloodpressureCat(Bp):
    if Bp<120:
        return 3;
    if Bp<140:
        return 4;
    return 1;
def CholesterolHigh(colValue):
    if colValue<200:
        return 2;
    return 1;
async def process_data(form_data,user):
        names=list(form_data.keys())
        form_data['Age Cat'],form_data['Age'],form_data['Gender'] =await age_cal_gender(user,True)  
        form_data['HighBloodPressure']=str(BloodpressureCat(int(form_data["BloodPressure"])))
        form_data['HighCholLevel']=str(CholesterolHigh(int(form_data["CholLevel"])))
        form_data["Weight"]=float(form_data["Weight"])
        form_data['bmi'] = BMI_cat(form_data['Height'],form_data['Weight'])     
        recorded,Record=await record(form_data,user)
        names.append('HighBloodPressure')
        names.append('HighCholLevel')
        for i in names:
            if i not in ['Weight']:
                form_data[i]=int(form_data[i])
                # print(int(form_data[i]))

        predictionVal,predicted=await prediction(form_data)
        
        if recorded and predicted:
            # print(predictionVal[0])
            cat,value=await prediction_cat(predictionVal[0],user)
            print(value)
            return True,cat,value,Record
        return False,np.NaN,0,{}    

async def prediction(formData):
    # try:
        with open("HeartHealth_classifier_model.pkl","rb") as f:
            model=pkl.load(f)
        names=[
               'PoorHealthDays',
               'HighBloodPressure',
               'RecentCholesterolCheck',
               'HighCholLevel',
               'KidneyDisease',
               'Diabetes',
               'DiabetesAge',
               'exercise',
               'Gender',
               'Age Cat',
               'bmi',
               'smoking',
               'Drinker']
        record=pd.DataFrame([formData])
        # record=np.array(record).reshape((1,-1))
        record=record[names]
        # print(list(record.values))
        predictionval=model.predict_proba(record)[:,1]
        # print(predictionval)
        return predictionval,True
    # except:
    #     return np.NaN,False
async def prediction_cat(value,username):
    if value==np.NaN:
        cat= ""
        
    elif value<0.16:
        cat= 'Low'
        value=value*100  * (33.33 / 16)
    elif value<0.35:
        cat= 'Medium'
        # print(33.33 + (value*100 - 16) * ((66.66 - 33.33) / 19))
        value=33.33 + (value*100  - 16) * ((66.66 - 33.33) / 19)
    else:
        cat='High'
        value=66.66 + (value*100  - 35) * ((100 - 66.66) / (100 - 35))
    client=pymongo.MongoClient(database_connection_string)
    db=client["Heart-health-dataBase"]
    coll=db["Users"]
    user=coll.find_one({"Username":username})
    coll.update_one(user,{"$set":{"prediction":value}})
    coll.update_one(user,{"$set":{"prediction-category":cat}})
    return cat,value
    

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

async def request_email(user,password):
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
async def change_password(password,username):
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

async def dieteryResponse(record):
    # try:

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a  diet planner for typical heart health, Just give the goals, recomendations and how to achieve them without any other uneccesary info and also compulsorily give the whole response in the form of a inner html part without html tag"},
                {"role": "user", "content": "Create a dietery plan for a patient with following abnormalities:\n "+str(record)}
            ]
        )
        # print(completion.choices[0].message)
        text=completion.choices[0].message.content

        # GOOGLE_API_KEY=f.decrypt(key).decode('utf-8')
        # genai.configure(api_key=GOOGLE_API_KEY)
        # model = genai.GenerativeModel('gemini-pro')
        # text='**'
        # while(re.search(r"\*\*",text)):
        #     response=model.generate_content('Create a dietery plan for a patient with following abnormalities:\n '+str(record)+ ',Just give the goals and how to achieve them and also compulsorily give the whole response in the form of a inner html part without html tag')
        #     text=response.text
        return True, text
    # except:
    #     return True, ''

async def process_data2(formData,user):
    model_name='model2_all.pkl'
    order=['age',
    'gender',
    'chest-pain',
    'restingbloodPressure',
    'cholestrol',
    'fasting-glucose-levels',
    'resting-ecg-result',
    'max-heart-rate',
    'angina-exercise',
    'oldpeak',
    'ST_slope',
    'major-vessels']

    formData["age"],formData['gender']=await age_cal_gender(user,False)
    if formData['oldpeak_unlock']!='1':
        del formData['ST-at-stress']
        del formData['ST-at-rest']
        order.remove('oldpeak')
        model_name='model2_without_Oldpeak.pkl'
    else:
        formData['oldpeak']=int(formData['ST-at-stress'])-int(formData['ST-at-rest'])
        
    if formData['coronaryAngiography']!='1':
        del formData['major-vessels']
        order.remove('major-vessels')
        if formData['oldpeak_unlock']!='1':
            model_name='model2_without_Oldpeak_caa.pkl'
        else:
            model_name='model2_without_caa.pkl'
    del formData['oldpeak_unlock']
    del formData['coronaryAngiography']
    # print(formData)

    flag,record=record_store(formData,user)
    if not flag:
        return '',0,"Unable to connect to database",{}
    for i in formData:            
        formData[i]=float(formData[i])
    if formData['fasting-glucose-levels']<=120:
        formData['fasting-glucose-levels']=0
    else:
        formData['fasting-glucose-levels']=1
    predictionVal=prediction_form2(formData,model_name,order)
    return prediction_cat2(predictionVal[0],user),predictionVal[0],'success',record

def prediction_form2(formdata,model_name,order):
    with open(model_name,'rb') as fh:
        model=pkl.load(fh)
    df=pd.DataFrame([formdata])
    df=df[order]
    return model.predict_proba(df)[:,0]
def record_store(data,username):
    try:
        record={}
        client = pymongo.MongoClient('mongodb+srv://heart_health-G64:heart_health-G64@cluster0.2tz5hzd.mongodb.net/')
        db = client['Heart-health-dataBase']
        cl=db['Users']
        user_cal={"Username":username}
        with open('name_values.json','r') as fh:
            names=json.load(fh)[0]
        data['gender']=str(data['gender'])
        # print(record,names)
        for name in data:
            if name not in names:
                record[name]=float(data[name])
                continue
            record[name]=names[name][data[name]]
        temp=record['gender']
        del record['gender']
        cl.update_one(user_cal,{"$set":{"record":record}})
        record['gender']=temp
        return True,record
    except:
        return False,{}

def prediction_cat2(value,username):
    if value<0.33:
        cat= 'Low'
    elif value<0.66:
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

def storediet(diet,username):
    try:
        client=pymongo.MongoClient(database_connection_string)
        db=client["Heart-health-dataBase"]
        coll=db["Users"]
        user=coll.find_one({"Username":username})
        coll.update_one(user,{"$set":{"diet":diet}})
        return True
    except:
        return False
        
