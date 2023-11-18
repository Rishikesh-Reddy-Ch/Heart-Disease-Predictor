from flask import Flask,render_template,request,flash,redirect,url_for,session,get_flashed_messages
import functions as fn
import pandas as pd
# import jsonify

app = Flask(__name__)
app.secret_key = 'secret-key'

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/register/',methods=['POST','GET'])
def register():
  if request.method == "POST":
    user=request.form
    if not fn.user_idCheck(user["Username"]):
      flash('Username already taken','error')
      return redirect(url_for('register'))
    
    elif not fn.passwordCheck(user["password"]):
      flash("Password must contain at least one uppercase, lowercase ,digit and a special character",'error')
      return redirect(url_for('register'))
      
    elif not fn.addressCheck(address=user["address"]):
       flash("Mension a valid pin-code in Address!",'error') 
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
           'DiabetesAge','smoking','exercise','HighCholLevel','Gender','Height','Weight','Drinker']
    formdata={}
    formdata.update(request.form)
    flag,predictionVal=fn.process_data(formdata,names,session["Username"])
    if (not flag):
      # flash("Unable to access the dataBase","error")
      return redirect(url_for("form"))
    return render_template("prediction.html",val=predictionVal)
  try:
    if session["Username"]:
      return render_template("form.html")
  except:
   return "Please "+ '<a href="'+url_for("login")+'"> login</a>'+' to continue'
   
  return render_template("form.html")

if __name__ == "__main__":
  app.run(debug=True)