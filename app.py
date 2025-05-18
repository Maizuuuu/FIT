from flask import Flask, render_template, request, session, redirect, url_for, flash
from models import db, User, Survey
from workout_logic import generate_workout_plan
import json

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db.init_app(app)

BANWORDS = ["admin", "root", "password", "123456", "qwerty"]


@app.route("/")
def welcome():
    return render_template("welcome.html")


@app.route("/registration", methods=["POST", "GET"])
def registerpage():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        errors = []  # Список для сбора всех ошибок

        # 1. Проверка заполненности полей
        if not username:
            errors.append("Поле имени пользователя обязательно")
        if not password:
            errors.append("Поле пароля обязательно")
        if not confirm_password:
            errors.append("Поле подтверждения пароля обязательно")

        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("registerpage"))

        # 2. Проверка длины
        if len(username) < 6:
            errors.append("Имя должно содержать минимум 6 символов")
        if len(password) < 6:
            errors.append("Пароль должен содержать минимум 6 символов")

        # 3. Проверка пробелов
        if " " in username:
            errors.append("Имя не должно содержать пробелов")
        if " " in password:
            errors.append("Пароль не должен содержать пробелов")

        # 4. Проверка банвордов
        if any(banned in username for banned in BANWORDS):
            errors.append("Имя содержит запрещенные слова")

        # 5. Проверка уникальности
        if User.query.filter_by(username=username).first():
            errors.append("Имя пользователя уже занято")

        # 6. Совпадение паролей
        if password != confirm_password:
            errors.append("Пароли не совпадают")

        # Если есть ошибки - показываем все
        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("registerpage"))

        # Создание пользователя
        try:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            session["user_id"] = new_user.id
            session["username"] = username
            return redirect("/")
        except Exception as e:
            db.session.rollback()
            flash("Ошибка при создании пользователя", "error")
            return redirect(url_for("registerpage"))


@app.route("/login", methods=["POST", "GET"])
def login_page():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        errors = []

        # Проверка заполненности
        if not username:
            errors.append("Поле имени пользователя обязательно")
        if not password:
            errors.append("Поле пароля обязательно")

        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("login_page"))

        user = User.query.filter_by(username=username).first()

        # Проверки существования и пароля
        if not user:
            errors.append("Пользователь с таким именем не найден")
        elif user.password != password:
            errors.append("Неверный пароль")

        if errors:
            for error in errors:
                flash(error, "error")
            return redirect(url_for("login_page"))

        session["user_id"] = user.id
        session["username"] = user.username
        return redirect("/")


@app.route("/logout")
def logout_page():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect("/login")


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    return render_template("profile.html", current_user=user)


@app.route("/delete-survey/<int:survey_id>", methods=["POST"])
def delete_survey(survey_id):
    if "user_id" not in session:
        return redirect("/login")

    survey = Survey.query.get(survey_id)

    # Проверка владельца
    if survey and survey.user_id == session["user_id"]:
        db.session.delete(survey)
        db.session.commit()
        flash("Опрос успешно удален", "success")
    else:
        flash("Ошибка удаления", "error")

    return redirect(url_for("profile"))


@app.route('/survey/weight-loss', methods=['GET', 'POST'])  # Добавляем оба метода
def weight_loss_survey():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        # Обработка данных формы из JS
        form_data = {
            'name': request.form['survey_name'],
            'age': request.form['age'],
            'current_weight': request.form['current_weight'],
            'target_weight': request.form['target_weight'],
            'activity': request.form['activity'],
            'health_issues': request.form.get('health_issues', 'no'),
            'restrictions': request.form.getlist('restrictions'),
            'workout_types': request.form.getlist('workout_types'),
            'workout_time': request.form['workout_time'],
            'score_total': request.form.get('score_total', 0),
            'score_base': request.form.get('score_base', 0),
            'score_activity': request.form.get('score_activity', 0),
            'score_health': request.form.get('score_health', 0),
            'score_preferences': request.form.get('score_preferences', 0)
        }
        
        plan = generate_workout_plan(
        total_score=int(form_data['score_total']),
        workout_types=form_data.getlist('workout_types'),
        workout_time=int(form_data['workout_time']),
        weight_diff=int(form_data['current_weight']) - int(form_data['target_weight'])
    )
        
        survey = Survey(
            name=form_data['name'],
            user_id=session['user_id'],
            survey_type='weight-loss',
            data=json.dumps(form_data),
            total_score=form_data['scores']['total']
        )
        db.session.add(survey)
        db.session.commit()
        
        return redirect("/survey_result")
    
    # GET-запрос: просто отображаем форму
    return render_template('survey_weight_loss.html')


# Маршрут для просмотра результата
@app.route("/survey-result/<int:survey_id>")
def view_survey_result(survey_id):
    if "user_id" not in session:
        return redirect("/login")

    survey = Survey.query.get(survey_id)

    if not survey or survey.user_id != session["user_id"]:
        flash("Опрос не найден", "error")
        return redirect(url_for("profile"))

    return render_template(
        "survey_result.html", survey=survey, result=json.loads(survey.result_data)
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
