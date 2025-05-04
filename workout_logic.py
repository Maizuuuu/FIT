from datetime import datetime

# База упражнений
EXERCISE_LIBRARY = {
    'bodyweight': {
        'beginner': [
            {'name': 'Приседания', 'muscles': ['ноги'], 'sets': 3, 'reps': 15},
            {'name': 'Отжимания от колен', 'muscles': ['грудь'], 'sets': 3, 'reps': 10}
        ],
        'intermediate': [
            {'name': 'Берпи', 'muscles': ['все тело'], 'sets': 4, 'reps': 12},
            {'name': 'Планка', 'muscles': ['кор'], 'duration': '30 сек'}
        ]
    },
    'dumbbells': {
        'full_body': [
            {'name': 'Приседания с гантелями', 'sets': 4, 'reps': 12},
            {'name': 'Тяга в наклоне', 'sets': 3, 'reps': 10}
        ]
    }
}

def calculate_tdee(data):
    """Рассчет суточного расхода калорий (Mifflin-St Jeor Equation)"""
    weight = float(data.get('weight', 70))  # Значения по умолчанию
    height = float(data.get('height', 170))
    age = int(data.get('age', 30))
    gender = data.get('gender', 'male')  # Используем get вместо прямого доступа
    
    if gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    activity_multiplier = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'high': 1.725
    }
    
    return bmr * activity_multiplier.get(data.get('activity_level', 'sedentary'), 1.2)

def get_equipment_exercises(equipment, level):
    """Подбор упражнений по инвентарю"""
    exercises = []
    
    if 'dumbbells' in equipment:
        exercises.extend(EXERCISE_LIBRARY['dumbbells']['full_body'])
    
    if 'resistance_band' in equipment:
        exercises.append({'name': 'Тяга эспандера', 'sets': 3, 'reps': 15})
    
    if not exercises:
        exercises = EXERCISE_LIBRARY['bodyweight'][level]
    
    return exercises

def generate_workout_plan(data):
    """Генерация полного плана"""
    plan = {}
    
    # 1. Расчет питания
    tdee = calculate_tdee(data)
    plan['nutrition'] = {
        'calories': tdee - 500,
        'protein': round(float(data['weight']) * 2.2, 1),
        'carbs': round((tdee * 0.4) / 4, 1)
    }
    
    # 2. Подбор тренировок
    level = 'beginner' if data['experience'] in ['beginner', '0-6 месяцев'] else 'intermediate'
    equipment = data.get('equipment', [])
    
    plan['workout'] = get_equipment_exercises(equipment, level)
    
    # 3. Рекомендации по восстановлению
    plan['recovery'] = {
        'sleep': 8 if data['fatigue_speed'] == 'high' else 7,
        'rest_days': max(2, 7 - int(data['desired_workouts']))
    }
    
    # 4. Ограничения по здоровью
    if 'back_pain' in data.get('health_issues', []):
        plan['restrictions'] = ['Исключить осевые нагрузки']
    
    return plan