from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import datetime
import sqlite3

import flask

app = Flask(__name__)
app.secret_key = "yeet"

"""
connection = sqlite3.connect("users.db")
cursor = connection.cursor()
cursor.execute("SELECT * FROM user;")
names = cursor.fetchall()
print(names)
"""

"""
connection = sqlite3.connect("users.db")
cursor = connection.cursor()
cursor.execute("ALTER TABLE listings ADD psw varchar(20);")
connection.commit()
connection.close()
"""
import flask_login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'


connection = sqlite3.connect("users.db")
cursor = connection.cursor()
sql_command = "SELECT email, pswhash FROM user;"
cursor.execute(sql_command)
details = cursor.fetchall()
users = {}
for detail in details:
    users[detail[0]] = detail[1]

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = check_password_hash(users[email], request.form['password'])

    return user



@app.route('/protected')
@flask_login.login_required
def protected():
    return render_template("success4.html")


@app.route("/")
def index():
    if flask_login.current_user.is_authenticated:
        connection = sqlite3.connect("users.db")
        cursor = connection.cursor()
        cursor.execute("SELECT xp FROM user WHERE email = '{}';".format(flask_login.current_user.id))
        xp = cursor.fetchall()[0][0]
        return render_template("index_main.html", xp=xp)
    else:
        return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")
@app.route("/register/check", methods=["POST"])
def register_check():
    
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    email = request.form.get("email")
    psw = request.form.get("psw")
    psw_repeat = request.form.get("psw-repeat")
    if psw != psw_repeat:
        return render_template("failure1.html")
    elif psw == psw_repeat:
        cursor.execute("SELECT email FROM user")
        emails = cursor.fetchall()
        found = False
        for i in emails:
            if i[0] == email:
                return render_template("failure1_1.html")
                found = True
                break                              
        if found == False:
            psw_hash = generate_password_hash(psw)
            cursor.execute("SELECT COUNT(*) FROM user;")
            count = cursor.fetchall()[0][0]
            sql_command = "INSERT INTO user VALUES ({}, '{}', '{}', 0);".format(str(count+1), email, psw_hash)
            cursor.execute(sql_command)
            connection.commit()
            connection.close()
            return render_template("success1.html")

@app.route("/location", methods=["POST"])
@flask_login.login_required
def location():
    loc = request.form.get("location")
    listings = []
    
    curr = datetime.datetime.now()
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM listings;")
    temp = cursor.fetchall()
    for e in temp:
        if e[4] == loc:
            listings.append(e)
    for listing in listings:
        datetime_obj = datetime.datetime.strptime(listing[3], '%Y-%m-%dT%H:%M')
        if curr >= datetime_obj:
            listings.remove(listing)      
    if loc == "north":
        return render_template("north.html", listings=listings)
    elif loc == "south":
        return render_template("south.html", listings=listings)
    elif loc == "east":
        return render_template("east.html", listings=listings)
    else:
        return render_template("west.html", listings=listings)


@app.route("/list")
@flask_login.login_required
def list():
    return render_template("list.html")

@app.route("/list/check", methods=["POST"])
@flask_login.login_required
def list_check():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    name = request.form.get("name")
    phone = request.form.get("phone")
    location = request.form.get("location")
    end = request.form.get("end")
    price = int(request.form.get("price"))
    psw = request.form.get("psw")
    if not name or not phone or not end or not location or not price or not psw:
        return render_template("failure3.html")
    else:
        cursor.execute("SELECT COUNT(*) FROM listings;")
        count = cursor.fetchall()[0][0]
        sql_command = "INSERT INTO listings VALUES ({}, '{}', '{}', '{}', '{}', {}, '{}');".format(str(count+1), name, phone, end, location, price, psw)
        cursor.execute(sql_command)
        connection.commit()
        connection.close()
        return render_template("success3.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return ''' 
                <style>
                    body{
                        background-color: #74bafc;
                    }

                    h1{
                        font-family: "UD Digi Kyokasho NK-B";
                        font-size: 30px;
                        text-align:center;
                    }                 
                    input:focus+label {
                        font-family: "UD Digi Kyokasho NK-B";
                        font-size: 15px;
                    }
                    body *{
                        font-family: "UD Digi Kyokasho NK-B";
                    }
                    input[type=text], input[type=password] {
                        width: 100%;
                        padding: 12px 20px;
                        margin: 8px 0;
                        display: inline-block;
                        border: 1px solid #ccc;
                        box-sizing: border-box;
                    }
                    button {
                        background-color: #4CAF50;
                        color: white;
                        padding: 14px 20px;
                        margin: 8px 0;
                        border: none;
                        cursor: pointer;
                        width: 100%;
                    }
                    button:hover {
                        opacity: 0.8;
                    }
                    .cancelbtn {
                        width: auto;
                        padding: 10px 18px;
                        background-color: #f44336;          
                    }
                    .imgcontainer {
                        text-align: right;
                        margin: 24px 0 12px 0;
                    }
                    .subbut {
                        opacity: 0.8;
                    }
                    span.psw {
                        float: right;
                        padding-top: 16px;
                    } 
                    @media screen and (max-width: 300px) {
                        span.psw {
                            display: block;
                            float: none;
                            }
                        .cancelbtn {
                            width: 100%;
                        }
                    }
                </style>
                <head><title>Login</title></head>
                <div class="container"> 
                <body>
                    <form action='login' method='POST'>
                    <div style="display: flex; justify-content: center; margin: 50px;">
                    <a href="/"><img src="/static/images/foodkoala.jpg" width="400" height="90" alt="FoodKoala"></a>
                    </div>
                    <h1>Login</h1>  
                    <label for="email"><b>Email</b></label>
                    <br>
                    <input type='text' name='email' id='email' placeholder='Key in email' style='border-radius: 15px 15px 15px 15px;'/>
                    <br>
                    <label for="psw"><b>Password</b></label>
                    <br>
                    <input type='password' name='password' id='password' placeholder='Key in password' style='border-radius: 15px 15px 15px 15px;'/>
                    <input type='submit' class='subbut' name='submit' style="float: right; width: auto; padding: 10px 18px; border-radius: 15px 15px 15px 15px; background-color: #1bff00;border: none; cursor: pointer; border: none;"/>
                    <button type="button" class="cancelbtn" style="border-radius: 15px 15px 15px 15px;"><a href = "/">Cancel</a></button>
                    </form>
                </body>
                </div>  
                '''


    email = flask.request.form['email']
    if check_password_hash(users[email], request.form['password']):
        user = User()
        user.id = email
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('protected'))
    else:
        return 'Bad Login'


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return render_template("success5.html")

@app.route("/mark", methods=["POST"])
@flask_login.login_required
def mark():
    psw = request.form.get("psw")
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM listings WHERE psw='{}'".format(psw))
    passwords = cursor.fetchall()[0]
    if passwords is None:
        return render_template("failure4.html")
    else:
        cursor.execute("DELETE FROM listings WHERE psw='{}'".format(psw))
        cursor.execute("SELECT xp FROM user WHERE email='{}';".format(flask_login.current_user.id))
        xp = int(cursor.fetchall()[0][0]) + 1
        cursor.execute("UPDATE user SET xp = {} WHERE email='{}';".format(xp, flask_login.current_user.id))
        connection.commit()
        connection.close()
        return render_template("success6.html")