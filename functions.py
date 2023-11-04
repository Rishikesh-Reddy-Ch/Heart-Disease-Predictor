import json
import re
from email_validator import validate_email
def user_idCheck(Username):
    with open("userInfo.json","r") as f:
        data=json.load(f)
        for user in data:
            if user["Username"]==Username:
                return False
    return True
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
    with open('userInfo.json', 'r') as f:
        data = json.load(f)
    for user in data:
        if user['Username'] == username and user['password'] == password:
            return True

    return False
def updateCredentials(Username,password,phoneNum,email):
    try:
        with open("userInfo.json","r+") as f:
            data=json.load(f)
        user={
                "Username":Username,
                "password":password,
                "phoneNum":phoneNum,
                "email":email  
        }
        data.append(user)
        with open("userInfo.json","w") as f:
            json.dump(data,f)
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

