from flask import Flask,render_template,request,flash,redirect,url_for,session,get_flashed_messages
import functions as fn
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
      fn.updateCredentials(username,password,phoneNum,email)
      return redirect(url_for('login'))
    
    else:
      flash("Invalid Phone Number or emailId",'error')

      return redirect(url_for('register'))
  return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == "GET":
#         username = request.args.get('username')
#         password = request.args.get('password')

        
#         user = fn.verify_credentials(username, password)
        
#         if user:
#             # session['user'] = username
#             return redirect(url_for('index'))

#         else:
#             flash('Invalid credentials, please try again.', 'error')
    
#     messages = get_flashed_messages();
#     return render_template('login.html',messages=messages)  
  
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = fn.verify_credentials(username, password)

        if user:
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.', 'error')
            return(redirect(url_for('login')))

    messages = get_flashed_messages()
    return render_template('login.html', messages=messages)

if __name__ == "__main__":
  app.run(debug=True)