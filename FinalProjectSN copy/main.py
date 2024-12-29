import hashlib
import uuid
from flask import Flask, render_template, request, redirect, url_for, make_response
from models import User, db, Message
import json

app = Flask(__name__)
db.create_all()

@app.route("/", methods=["GET"])
def index():
    messages = db.query(Message).all()
    session_token = request.cookies.get("session_token")
    user = None

    with open("countires.json", "r") as file:
        countries_data = json.load(file)

    if session_token:
        user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    if user:
        return render_template("index.html", user=user, messages=messages, countries_data=countries_data)
    else:
        return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    email = request.form.get("user-email")
    password = request.form.get("user-password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    user = db.query(User).filter_by(email=email).first()

    if not user:
        return "User does not exist"
    
    if hashed_password != user.password:
        return "Wrong password"
    
    session_token = str(uuid.uuid4())
    user.session_token = session_token
    user.save()

    response = make_response(redirect(url_for("index")))
    response.set_cookie("session_token", session_token)
    return response

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("user-name-register")
    email = request.form.get("user-email-register")
    country = request.form.get("user-country-register")
    password = request.form.get("user-password-register")
    repeat_password = request.form.get("user-repeat-password-register")

    if password != repeat_password:
        return "Passwords do not match"
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    existing_user = db.query(User).filter_by(email=email).first()
    if existing_user:
        return "User already exists"
    
    new_user = User(name=name, email=email, country=country, password=hashed_password)
    new_user.save()

    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    response = make_response(redirect(url_for("login")))
    response.delete_cookie("session_token")
    return response

@app.route("/add-message", methods=["POST"])
def add_message():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()
    user_name = user.name
    user_country = user.country
    text = request.form.get("text")
    print("{0}:{1}".format(user_name, text))

    message = Message(author=user_name, authors_country=user_country, message=text)
    message.save()

    return redirect("/")

@app.route("/profile", methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")

    # get user from database based on session_token
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    if user:
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("index"))

@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    session_token = request.cookies.get("session_token")

    # get user from database based on session_token
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    if request.method == "GET":
        if user:
            return render_template("profile_edit.html", user=user)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        name = request.form.get("profile-name")
        email = request.form.get("profile-email")

        # update user object
        user.name = name
        user.email = email

        # store changes into database
        user.save()
        return redirect(url_for("profile"))
    
@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")

    # get user from the database based on session_token
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    if request.method == "GET":
        if user:
            return render_template("profile_delete.html", user=user)
        else:
            return redirect(url_for("index"))
    elif request.method == "POST":
        # delete user in databse
        user.deleted = True
        user.save()

        return redirect(url_for("index"))

@app.route("/users", methods=["GET"])
def all_users():
    users = db.query(User).filter_by(deleted=False).all()

    return render_template("users.html", users=users)

@app.route("/user/<user_id>", methods=["GET"])
def user_details(user_id):
    user = db.query(User).get(int(user_id))

    return render_template("user_details.html", user=user)

if __name__ == "__main__":
    app.run(use_reloader=True, port=5010)