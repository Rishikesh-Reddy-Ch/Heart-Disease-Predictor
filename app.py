from flask import Flask,render_template,request,flash,redirect,url_for,session,get_flashed_messages
import functions as fn
import pandas as pd
# import jsonify

app = Flask(__name__)
app.secret_key = 'secret-key'

@app.route('/')
def index():
  return render_template('app.html')

@app.route('/register',methods=['POST','GET'])
def register():
  if request.method == "POST":
    username = request.form['username']
    password = request.form['password']
    phoneNum = request.form['phoneNum']
    email = request.form['email']
    if not fn.user_idCheck(username):
      flash('Username already taken','error')
      return redirect(url_for('register'))
    
    elif not fn.passwordCheck(password):
      flash("Password must contain at least one uppercase, lowercase ,digit and a special character",'error')
      return redirect(url_for('register'))
      
    elif  fn.numCheck(phoneNum) and  fn.emailValidate(email):
      updated=fn.updateCredentials(username,password,phoneNum,email)
      if not updated:
         flash("Unable to connect to database","error")
         return redirect(url_for('register'))
      return redirect(url_for('login'))
    
    else:
      flash("Invalid Phone Number or emailId",'error')

      return redirect(url_for('register'))
  return render_template('register.html',messages=get_flashed_messages(with_categories=True))

  
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = fn.verify_credentials(username, password)

        if user:
            session["Username"]=username
            return redirect(url_for('form'))
        else:
            flash('Invalid credentials, please try again.', 'error')
            return(redirect(url_for('login')))

    messages = get_flashed_messages()
    return render_template('login.html', messages=messages)
@app.route('/form',methods=['GET','POST'])
def form():
  if request.method=='POST':
    names=['HadHeartAttack','HighBloodPressure','AnyHeartStroke','KidneyDisease','Diabetis','DiabetesAge','smoking','exercise','HighCholLevel','Gender','DateOfBirth','Height','Weight','Drinker']
    formdata={}
    for i in names:
      formdata[i]=request.form[i]
    if not fn.process_data(formdata,names,session["Username"]):
       flash("Unable to access the dataBase","error")
       return redirect(url_for("form"))
  return render_template("form.html")
if __name__ == "__main__":
  app.run(debug=True)