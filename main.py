from flask import Flask,render_template,request,flash,redirect,url_for,session,get_flashed_messages,jsonify
import functions as fn
import pandas as pd
import random
import numpy as np
import asyncio
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, redirect, session,request

app = Flask(__name__)
app.secret_key = 'secret-key'
oauth = OAuth(app)


google = oauth.register(
    name='google',
    client_id='121737871171-5603if7oi2reg13gkg2pfgh94ucjd5mh.apps.googleusercontent.com',
    client_secret="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",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid profile email https://www.googleapis.com/auth/user.gender.read https://www.googleapis.com/auth/user.birthday.read'},
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    _AUTHORIZE_PARAMS={'approval_prompt': 'auto'}  
)
# import jsonify
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='hearthealth.g64@gmail.com',
    MAIL_PASSWORD='xzjc fxxd rxaw qafz'
)
mail = Mail(app)
@app.route('/')
async def home():
  return render_template('home.html')


@app.route('/about')
async def about():
  return render_template('about.html')

@app.route('/register/usercheck/',methods=['POST'])
async def usercheck():
  user=request.json["UserID"]
  flag,msg=await fn.user_idCheck(user)
  if flag:
    valid=True
  else:
    valid=False
  response = jsonify({"valid": valid,"msg":msg})
  return response

@app.route('/login/method/')
async def signinMethod():
  # print(url_for('googlelogin'))
  return render_template('SignIn_options.html')

@app.route('/login/googlelogin/')
async def googlelogin():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    
    return google.authorize_redirect(redirect_uri, approval_prompt='auto')

@app.route('/authorize')
async def authorize():
    try:
      google = oauth.create_client('google')
      token =  google.authorize_access_token()
      resp1 =  google.get('userinfo')

      user_info1 = resp1.json()
      # print(user_info1)
      
      flag,msg=await fn.user_idCheck(user_info1['name'])
      if msg:
        return msg
      if not flag:
        session['Username']=user_info1.get('name',None)
        # print(user_info1['name'])
      else:
      
        resp2 = google.get('https://people.googleapis.com/v1/people/me?personFields=genders,birthdays')
        user_info2=resp2.json()
        gender_info = user_info2.get('genders', [{}])[0].get('formattedValue', None)
        birthday_info = user_info2.get('birthdays', [{}])[0].get('date', {})
        birthday=str(birthday_info['year'])+'-'+str(birthday_info['month'])+'-'+ str(birthday_info['day'])
        user_info={}
        user_info.update({'gender':gender_info})
        user_info.update({'Username':user_info1.get('name',None)})
        user_info.update({'dob':birthday})
        user_info.update({'email':user_info1.get('email',None)})
        user_info.update({'password':'GoogleUser'})
        for i in user_info:
          if not user_info[i]:
            return "unable to obtain your account info, "+ '<a href="'+url_for("googlelogin")+'">try relogin</a>'
        updated=await fn.updateCredentials(user_info)
        session['Username']=user_info['Username']
        del user_info2,user_info
        del user_info1  
    except:
      return "unable to obtain your account info, "+ '<a href="'+url_for("googlelogin")+'">try relogin</a>'
      
    return redirect(url_for('home'))

@app.route('/register/',methods=['POST','GET'])
async def register():
  if request.method == "POST":
    user=request.form   
  
    updated=await fn.updateCredentials(user)
    if not updated:
      flash("Unable to connect to database","error")
      return redirect(url_for('register'))
    return redirect(url_for('login'))
  try:
      if session["Username"]:
        return "Already logged in, "+ '<a href="'+url_for("logout")+'"> logout</a>'+' to register a new account.'
  except:
    return render_template('register.html',messages=get_flashed_messages())
  return render_template('register.html',messages=get_flashed_messages())

@app.route('/register/email-validate/',methods=['POST'])
async def emailValidate():
  email=request.json['email']
  if fn.emailValidate(email):
    return jsonify({'valid':True})
  return jsonify({'valid':False})


@app.route('/login/', methods=['GET', 'POST'])
async def login():
    if request.method == "POST":
        user=request.form

        isuser,msg =await fn.verify_credentials(user["Username"], user["password"])

        if isuser:
            session["Username"]=user["Username"]
            return redirect(url_for('home'))
        else:
            if msg:
              flash(msg,'error')
            else:
              flash('Invalid credentials, please try again.', 'error')
            return(redirect(url_for('login')))

    messages = get_flashed_messages()
    try:
      if session["Username"]:
          return "Already logged in, "+ '<a href="'+url_for("home")+'"> go to home page</a>'
    except:
       return render_template('login.html', messages=messages)
    return render_template('login.html', messages=messages)

@app.route('/logout/')
async def logout():
   if "Username" in session:
    session.pop("Username")
   return redirect(url_for('home'))

@app.route('/med_form/',methods=['GET','POST'])
async def form2():
  if request.method=='POST':
    form_data={}
    form_data.update(request.form)
    cat,percent,Message,record=fn.process_data2(form_data,session['Username'])
    session['record']=record
    # print(cat,percent,Message,record)
    print(percent,Message)
    # return redirect(url_for('result',cat=cat))
  try:
    if session["Username"]:
      return render_template("form.html")
  except:
   return "Please "+ '<a href="'+url_for("login")+'"> login</a>'+' to continue'

@app.route('/form/',methods=['GET','POST'])
async def form():
  if request.method=='POST':
    formdata={}
    formdata.update(request.form)
    flag,predictioncat,percent,record=await fn.process_data(formdata,session["Username"])
    if (not flag):
      # flash("Unable to access the dataBase","error")
      return redirect(url_for("form"))
    session['record']=record
    return redirect(url_for('result',cat=predictioncat,percent=int(percent)))
    # return "percent: "+str(percent)
  try:
    if session["Username"]:
      return render_template("form1.html")
  except:
   return "Please "+ '<a href="'+url_for("login")+'"> login</a>'+' to continue'
   
  return render_template("form1.html")

@app.route("/result<cat>&<percent>/",methods=["GET"])
async def result(cat,percent):
  if cat=="High":
    # retrived,dietplan=fn.dieteryResponse(session['record'])
    return render_template("prediction_high.html",prediction=cat,percent=str(round(float(percent),ndigits=2)))
  elif cat=="Medium":
    # retrived,dietplan=fn.dieteryResponse(session['record'])
    return render_template("prediction_medium.html",prediction=cat,percent=str(round(float(percent),ndigits=2)))
  elif cat=='Low':
    return render_template("prediction_low.html",percent=str(round(float(percent),ndigits=2)),prediction=cat)
  else:
    return redirect(url_for('form'))

@app.route("/result/requestDietPlan/")
async def requestDietPlan():
  retrived,dietplan=await fn.dieteryResponse(session['record'])
  return jsonify({'retrived':retrived,'dietplan':dietplan})

@app.route('/address_check/', methods=["POST"])
async def addess_checking():
    pin_code=request.json["pin-code"]
    result=await fn.addressCheck(pin_code)
    response = jsonify({"valid": result})
    return response

@app.route('/changePassword/')
async def changePassword():
  return render_template('change_password.html',messages=get_flashed_messages())

@app.route('/changePassword/generateotp/',methods=['POST'])
async def generateotp():
    email,error=await fn.request_email(request.json["username"],request.json['password'])
    response={'generated':True,'error':None}
    if email:
      otp=random.randint(100000,999999)
      with mail.connect() as conn:
        message = Message(
            'Password Change OTP Request',
            sender='cherukurishi95@gmail.com',
            recipients=[email],
            body="Dear %s, \n\nYou've requested to reset your password for your  account. To proceed, please use the following OTP to verify your identity and set a new password.\n\nOne-Time Password (OTP): %d"%(request.json["username"],otp)
        )
        session['OTP']=str(otp);
        conn.send(message)
        
    else:
      response['error']=error
      response['generated']=False
    return jsonify(response)


@app.route('/changePassword/otpvalidation/',methods=['POST'])
async def otpValidation():
  response={'changed':True,'error':'success'}
  # print(session['OTP'],request.json['OTP'])
  if not fn.passwordCheck(request.json['password']):
    response['changed']=False
    response['error']="Password needs: Uppercase, Lowercase, Digit, Special Char."
 
  elif(session['OTP']!=request.json['OTP']):
    response['changed']=False
    response['error']="Enter valid otp"
  else:
    response['changed'],response['error']=await fn.change_password(request.json['password'],request.json['username'])
  if(response['changed']):
    session.pop('OTP')
  return jsonify(response)

@app.route('/dietStore/',methods=['POST'])
async def dietStore():
  diet=request.json["dietStore"]
  return jsonify({'stored':await fn.storediet(diet,session["Username"])})
if __name__ == "__main__":
  app.run(debug=True,threaded=True)