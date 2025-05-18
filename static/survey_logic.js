function calculateScores(formData) {
  const scores = {
    base: 0,
    activity: 0,
    health: 0,
    preferences: 0,
    total: 0
  };

  // 1. Базовые показатели (30% от общего)
  scores.base = Math.round(
    (parseInt(formData.age) * 0.2 + 
    (parseInt(formData.current_weight) - parseInt(formData.target_weight)) * 0.5
  ));

  // 2. Активность (25%)
  switch(formData.activity) {
    case 'low': scores.activity = 10; break;
    case 'medium': scores.activity = 20; break;
    case 'high': scores.activity = 30; break;
  }

  // 3. Здоровье (20%, штрафы)
  if (formData.health_issues === 'yes') {
    scores.health = -15;
    if (formData.restrictions?.includes('heart')) scores.health -= 5;
    if (formData.restrictions?.includes('joints')) scores.health -= 5;
  }

  // 4. Предпочтения (25%)
  if (formData.workout_types.includes('cardio')) scores.preferences += 10;
  if (formData.workout_types.includes('strength')) scores.preferences += 15;

  // Итог
  scores.total = Math.max(0, scores.base + scores.activity + scores.health + scores.preferences);
  return scores;
}

// Обработка формы
document.querySelector('form').addEventListener('submit', function(e) {
  e.preventDefault();
  
  const formData = {
    survey_name: this.querySelector('[name="survey_name"]').value,
    age: this.querySelector('[name="age"]').value,
    current_weight: this.querySelector('[name="current_weight"]').value,
    target_weight: this.querySelector('[name="target_weight"]').value,
    activity: this.querySelector('[name="activity"]:checked')?.value,
    health_issues: this.querySelector('[name="health_issues"]:checked')?.value,
    restrictions: Array.from(this.querySelectorAll('[name="restrictions"]:checked')).map(el => el.value),
    workout_types: Array.from(this.querySelectorAll('[name="workout_types"]:checked')).map(el => el.value),
    workout_time: this.querySelector('[name="workout_time"]').value
  };

  const scores = calculateScores(formData);
  
  // Добавляем скрытые поля
  for (const [key, value] of Object.entries(scores)) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = `score_${key}`;
    input.value = value;
    this.appendChild(input);
  }

  this.submit();
});

function submitForm(scores) {
  const form = document.querySelector('form');
  
  // Удаляем предыдущие скрытые поля
  document.querySelectorAll('input[type="hidden"]').forEach(el => el.remove());
  
  // Добавляем новые поля
  Object.entries(scores).forEach(([key, value]) => {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = `score_${key}`;
    input.value = value;
    form.appendChild(input);
  });

  // Добавляем лог для отладки
  console.log('Отправляемые данные:', Array.from(new FormData(form)));
  
  form.submit();
}