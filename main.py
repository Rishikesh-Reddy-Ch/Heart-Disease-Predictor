from flask import Flask,render_template,request,flash,redirect,url_for,session,get_flashed_messages
import functions as fn
import pandas as pd
import random
import numpy as np
# import jsonify

app = Flask(__name__)
app.secret_key = 'secret-key'

@app.route('/')
def home():
  return render_template('home.html')


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
# @app.roulte('/password-change/',methods=['GET','POST'])
# def forgot_pass():
#   if request.method=='POST':
#     email = request.form['email']
#     user_otp = request.form['otp']

    
  
#   return render_template("otp.html")
# @app.roulte('/email-validate/',methods=['GET'])
# def validate():
#    otp=str(random.randint(100000, 999999))
@app.route("/result<cat>/",methods=["GET"])
def result(cat):
  if cat=="High":
    # predictionVal=np.NaN
    return render_template("prediction_high.html")
  elif cat=="Medium":
    return render_template("prediction_medium.html")
  elif cat=='Low':
    return render_template("prediction_low.html")
  else:
    return redirect(url_for('form'))
  
# @app.route('/')

      

   

if __name__ == "__main__":
  app.run(debug=True)