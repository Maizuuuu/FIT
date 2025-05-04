from flask import Flask, render_template, request, session, redirect, url_for, flash
from models import db, User, Workout  
from workout_logic import calculate_tdee, generate_workout_plan, get_equipment_exercises

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

BANWORDS = ['admin', 'root', 'password', '123456', 'qwerty']

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

        # Проверка через SQLAlchemy
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template("register.html", error="Имя пользователя уже занято")
        
        if password != confirm_password:
            return render_template("register.html", error="Пароли не совпадывают")

        # Создание нового пользователя
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        session["user_id"] = new_user.id
        return redirect("/")
    

@app.route("/login", methods=["POST", "GET"])
def login_page():
    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Используем исправленный метод
        user = User.query.filter_by(username=username).first()
        
        if not user or user.password != password:
            return render_template("login.html", error='Неправильный логин или пароль')
        if not username or not password:
            flash('Все поля обязательны для заполнения', 'error')
            return redirect('/login')
        session["user_id"] = user.id
        return redirect('/')



@app.route("/logout")
def logout_page():
    session.pop("username", None)
    return redirect("/login")

def calculate_tdee(data):
    """Рассчет ежедневного расхода калорий (Mifflin-St Jeor Equation)"""
    weight = float(data['weight'])
    height = float(data['height'])
    age = int(data['age'])
    
    if data['gender'] == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    activity_multiplier = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'high': 1.725
    }
    
    return bmr * activity_multiplier[data['activity_level']]

def generate_workout_plan(data):
    plan = {}
    
    # Расчет целевого дефицита калорий
    tdee = calculate_tdee(data)
    deficit = 500 if data['desired_workouts'] >= 4 else 300
    plan['calories'] = tdee - deficit
    
    # Подбор типа тренировок
    if data['experience'] == 'beginner':
        plan['type'] = 'full_body'
        plan['days'] = 3
    else:
        plan['type'] = 'split'
        plan['days'] = data['desired_workouts']
    
    # Учет ограничений по здоровью
    if 'back_pain' in data['health_issues']:
        plan['restrictions'] = ['no_heavy_lifting', 'core_focus']
    
    # Подбор упражнений
    equipment = data['equipment']
    if 'none' in equipment:
        plan['exercises'] = get_bodyweight_exercises(data['focus_areas'])
    else:
        plan['exercises'] = get_equipment_exercises(equipment)
    
    # Рекомендации по восстановлению
    plan['recovery'] = {
        'sleep': 8 if data['fatigue_speed'] == 'high' else 7,
        'rest_days': max(2, 7 - int(data['desired_workouts']))
    }
    
    return plan

@app.route('/survey/weight-loss', methods=['GET', 'POST'])
def weight_loss_survey():
    # Проверка авторизации
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    # Обработка GET-запроса
    if request.method == 'GET':
        return render_template('survey_weight_loss.html')

    # Обработка POST-запроса
    try:
        # Сбор и преобразование данных формы
        data = {
            # Личные данные
            'name': request.form.get('name', ''),
            'age': int(request.form.get('age', 25)),
            'gender': request.form.get('gender', 'male'),
            'height': float(request.form.get('height', 170)),
            'weight': float(request.form.get('weight', 70)),
            'chest': float(request.form.get('chest', 0)) if request.form.get('chest') else None,
            'waist': float(request.form.get('waist', 0)),
            'hips': float(request.form.get('hips', 0)) if request.form.get('hips') else None,
            
            # Параметры тренировок
            'fatigue_speed': request.form.get('fatigue_speed', 'medium'),
            'workout_duration': int(request.form.get('workout_duration', 30)),
            'experience': request.form.get('experience', 'beginner'),
            'workouts_per_week': int(request.form.get('workouts_per_week', 3)),
            
            # Здоровье и активность
            'activity_level': request.form.get('activity_level', 'sedentary'),
            'health_issues': request.form.getlist('health_issues'),
            
            # Цели и оборудование
            'desired_workouts': int(request.form.get('desired_workouts', 3)),
            'location': request.form.get('location', 'home'),
            'equipment': request.form.getlist('equipment'),
            
            # Дополнительная информация
            'focus_areas': request.form.getlist('focus_areas'),
            'current_plan': request.form.get('current_plan', ''),
            'habits': request.form.getlist('habits'),
            'comments': request.form.get('comments', '')
        }

        # Генерация плана тренировок
        plan = generate_workout_plan(data)

        # Создание записи в БД
        new_workout = Workout(
            user_id=session['user_id'],
            goal='weight_loss',
            data=data,
            plan=plan
        )

        db.session.add(new_workout)
        db.session.commit()

        return redirect(url_for('result', workout_id=new_workout.id))

    except ValueError as e:
        db.session.rollback()
        return render_template('error.html', 
                             error=f"Ошибка ввода данных: {str(e)}")

    except KeyError as e:
        db.session.rollback()
        return render_template('error.html', 
                             error=f"Отсутствует обязательное поле: {str(e)}")

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Ошибка при сохранении: {str(e)}")
        return render_template('error.html', 
                             error="Произошла внутренняя ошибка сервера")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)