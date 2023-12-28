from flask import Flask,render_template,request,flash,redirect,url_for,session,get_flashed_messages,jsonify
import functions as fn
import pandas as pd
import random
import numpy as np
from flask_mail import Mail, Message

# import jsonify
def session_username():
  try:
    if session['Username']:
      return True
    return False
  except:
    return False

app = Flask(__name__)

app.secret_key = 'secret-key'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='hearthealth.g64@gmail.com',
    MAIL_PASSWORD='xzjc fxxd rxaw qafz'
)
mail = Mail(app)
@app.route('/')
def home():
  return render_template('home.html',user=session_username())


@app.route('/about')
def about():
  return render_template('about.html')


@app.route('/register/',methods=['POST','GET'])
def register():
  if request.method == "POST":
    user=request.form
    if not fn.user_idCheck(user["Username"]):
      flash('Username already taken','error')
      return redirect(url_for('register'))
    
    elif not fn.passwordCheck(user["password"]):
      flash("Password needs: Uppercase, Lowercase, Digit, Special Char.",'error')
      return redirect(url_for('register'))
    
    elif fn.emailValidate(user["email"]) and fn.dob_validate(user["dob"]):
      updated=fn.updateCredentials(user)
      if not updated:
         flash("Unable to connect to database","error")
         return redirect(url_for('register'))
      return redirect(url_for('login'))
    
    else:
      flash("Invalid email or Date-of-birth",'error')

      return redirect(url_for('register'))
  try:
      if session["Username"]:
        return "Already logged in, "+ '<a href="'+url_for("logout")+'"> logout</a>'+' to register a new account.'
  except:
    return render_template('register.html',messages=get_flashed_messages())
  return render_template('register.html',messages=get_flashed_messages())

  
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user=request.form

        isuser = fn.verify_credentials(user["Username"], user["password"])

        if isuser:
            session["Username"]=user["Username"]
            return redirect(url_for('home'))
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
def logout():
   if "Username" in session:
    session.pop("Username")
   return redirect(url_for('home'))

@app.route('/form/',methods=['GET','POST'])
def form():
  if request.method=='POST':
    names=['HadHeartAttack','HighBloodPressure','AnyHeartStroke','KidneyDisease','Diabetes',
           'DiabetesAge','smoking','exercise','HighCholLevel','Height','Weight','Drinker']
    formdata={}
    formdata.update(request.form)
    flag,predictionVal=fn.process_data(formdata,names,session["Username"])
    if (not flag):
      # flash("Unable to access the dataBase","error")
      return redirect(url_for("form"))
    return redirect(url_for('result',cat=predictionVal))
  try:
    if session["Username"]:
      return render_template("form.html")
  except:
   return "Please "+ '<a href="'+url_for("login")+'"> login</a>'+' to continue'
   
  return render_template("form.html")

@app.route("/result<cat>/",methods=["GET","POST"])
def result(cat):
  if cat=="High":
    if request.method=="POST":
      zipCode=request.form["user-address"]
      if fn.addressCheck(zipCode):
        location=request.form["location"]
        return render_template('prediction_high.html',)
    # predictionVal=np.NaN
    return render_template("prediction_high.html")
  elif cat=="Medium":
    return render_template("prediction_medium.html")
  elif cat=='Low':
    return render_template("prediction_low.html")
  else:
    return redirect(url_for('form'))
  
@app.route('/address_check/', methods=["POST"])
def addess_checking():
    pin_code=request.json["pin-code"]
    result=fn.addressCheck(pin_code)
    response = jsonify({"valid": result})
    return response

@app.route('/changePassword/')
def changePassword():
  return render_template('change_password.html',messages=get_flashed_messages())

@app.route('/changePassword/generateotp/',methods=['POST'])
def generateotp():
    email,error=fn.request_email(request.json["username"],request.json['password'])
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
def otpValidation():
  response={'changed':True,'error':'success'}
  # print(session['OTP'],request.json['OTP'])
  if not fn.passwordCheck(request.json['password']):
    response['changed']=False
    response['error']="Password needs: Uppercase, Lowercase, Digit, Special Char."
 
  elif(session['OTP']!=request.json['OTP']):
    response['changed']=False
    response['error']="Enter valid otp"
  else:
    response['changed'],response['error']=fn.change_password(request.json['password'],request.json['username'])
  if(response['changed']):
    session.pop('OTP')
  return jsonify(response)

   

if __name__ == "__main__":
  app.run(debug=True)