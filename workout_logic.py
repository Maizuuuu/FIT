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

def generate_workout_plan(total_score, workout_types, workout_time, weight_diff):
    """Главная функция генерации плана тренировок"""
    level = _get_level(total_score)
    equipment = _get_available_equipment(workout_types)
    
    return {
        'level': level['name'],
        'workouts_per_week': level['workouts'],
        'workout_time': _calculate_time(workout_time, level),
        'exercises': _select_exercises(level, equipment),
        'estimated_weeks': _calculate_weeks(weight_diff, total_score),
        'color': level['color']
    }

def _get_level(score):
    """Определение уровня подготовки"""
    if score < 30:
        return {'name': 'beginner', 'workouts': 3, 'color': '#ff6b6b'}
    elif score < 60:
        return {'name': 'intermediate', 'workouts': 4, 'color': '#feca57'}
    return {'name': 'advanced', 'workouts': 5, 'color': '#1dd1a1'}

def _get_available_equipment(workout_types):
    """Получение доступного оборудования"""
    equipment = []
    if 'cardio' in workout_types:
        equipment.append('bodyweight')
    if 'strength' in workout_types:
        equipment.append('dumbbells')
    return equipment

def _select_exercises(level, equipment):
    """Выбор упражнений из библиотеки"""
    exercises = []
    for eq in equipment:
        category = EXERCISE_LIBRARY.get(eq, {})
        
        # Ищем упражнения для текущего уровня
        if level['name'] in category:
            exercises.extend(category[level['name']])
        
        # Добавляем упражнения full_body если есть
        if 'full_body' in category:
            exercises.extend(category['full_body'])
    
    return _format_exercises(exercises)[:4]  # Не более 4 упражнений

def _format_exercises(exercises):
    """Форматирование описания упражнений"""
    formatted = []
    for ex in exercises:
        if 'duration' in ex:
            desc = f"{ex['name']} ({ex['duration']})"
        else:
            desc = f"{ex['name']} {ex['sets']}×{ex['reps']}"
        formatted.append(desc)
    return formatted

def _calculate_time(base_time, level):
    """Расчет времени тренировки"""
    time_adjustment = {
        'beginner': -5,
        'intermediate': 0,
        'advanced': 10
    }.get(level['name'], 0)
    
    return 5 * round((base_time + time_adjustment) / 5)

def _calculate_weeks(weight_diff, score):
    """Расчет срока достижения цели"""
    base_weeks = max(2, round((weight_diff * 0.7) / (score / 20)))
    return f"{base_weeks}-{base_weeks + 2} недель"