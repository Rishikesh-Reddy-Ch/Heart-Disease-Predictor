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

@app.route('/register/usercheck/',methods=['POST'])
def usercheck():
  user=request.json["UserID"]
  flag,msg=fn.user_idCheck(user)
  if flag:
    valid=True
  else:
    valid=False
  response = jsonify({"valid": valid,"msg":msg})
  return response

@app.route('/register/',methods=['POST','GET'])
def register():
  if request.method == "POST":
    user=request.form   
  
    updated=fn.updateCredentials(user)
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
def emailValidate():
  email=request.json['email']
  if fn.emailValidate(email):
    return jsonify({'valid':True})
  return jsonify({'valid':False})


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user=request.form

        isuser,msg = fn.verify_credentials(user["Username"], user["password"])

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
def logout():
   if "Username" in session:
    session.pop("Username")
   return redirect(url_for('home'))

@app.route('/med_form/',methods=['GET','POST'])
def form2():
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
def form():
  if request.method=='POST':
    formdata={}
    formdata.update(request.form)
    flag,predictioncat,percent,record=fn.process_data(formdata,session["Username"])
    if (not flag):
      # flash("Unable to access the dataBase","error")
      return redirect(url_for("form"))
    session['record']=record
    
    return redirect(url_for('result',cat=predictioncat,percent=percent))
    # return "percent: "+str(percent)
  try:
    if session["Username"]:
      return render_template("form1.html")
  except:
   return "Please "+ '<a href="'+url_for("login")+'"> login</a>'+' to continue'
   
  return render_template("form1.html")

@app.route("/result<cat>&<percent>/",methods=["GET"])
def result(cat,percent):
  if cat=="High":
<<<<<<< HEAD
    # if request.method=="POST":
    #   zipCode=request.form["user-address"]
    #   if fn.addressCheck(zipCode):
    #     location=request.form["location"]
    # return render_template('prediction_high.html',)
    # predictioncat=np.NaN
    retrived,dietplan=fn.dieteryResponse(session['record'])
    return render_template("prediction_high.html",message=dietplan)
=======
    return render_template("prediction_high.html")
>>>>>>> b0a4004593f9ae868c6d4a43613e1f095b8ce478
  elif cat=="Medium":
    retrived,dietplan=fn.dieteryResponse(session['record'])
    return render_template("prediction_medium.html",message=dietplan)
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

<<<<<<< HEAD
@app.route('/dietStore/',methods=['POST'])
def dietStore():
  diet=request.json["dietStore"]
  return jsonify({'stored':fn.storediet(diet,session["Username"])})
=======
@app.route('/googleUserLogin/',methods=['GET'])
def googleUserLogin():
  return render_template('temp.html')

>>>>>>> b0a4004593f9ae868c6d4a43613e1f095b8ce478
if __name__ == "__main__":
  app.run(debug=True)