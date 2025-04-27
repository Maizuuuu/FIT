from flask import Flask, render_template, request, redirect, session
from models import db, User

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/registration", methods=["POST", "GET"])
def registerpage():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form.get("username").lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        user = User.getbyusername(username)
        if user:
            return render_template("register.html", error="Имя пользователя уже занято")
        if password != confirm_password:
            return render_template("register.html", error="Пароли не совпадают")

        User.create(username, password)
        session["username"] = username
        return redirect("/")

@app.route("/login", methods=["POST", "GET"])
def login_page():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.getbyusername(username)
        if not user or user.password != password:
            return render_template("login.html", error="Неправильный логин или пароль")

        session["username"] = username
        return redirect("/")

@app.route("/logout")
def logout_page():
    session.pop("username", None)
    return redirect("/login")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)