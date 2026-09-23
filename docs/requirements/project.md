Список інструментів: .venv, ruff, pylance,

Ціль - продемоснтурвати ШІ.

Скоуп:
В: Гра проти комп'ютера на одному пристрої, локальний UI.
Аут: Мультиплеєр по мережі, гра людина-проти-людини, 3D-графіка, мобільна версія.

Критерії приймання (Acceptance Criteria): Проєкт вважається успішним, якщо: програма запускається без крашів, користувач може провести повну партію від початку до кінця, алгоритм ШІ завжди блокує очевидний виграшний хід гравця (не робить дурних помилок).

типізувати сигнатури функцій та моделі даних, якийсь лінтер (Pyright, Ruff?), Type Hints, frozen=True, list / tuple, set / frozenset
1.0: Думаю трейтів не буде, але якщо будуть, тоді Protocol

Для Вичерпності match/case mypy, чи є щось в поточних існтурментах?
Берем pyright, найкраще для vscode. Увімкнути Strict.

Для Option Optional[T] чи T | None?
Лише T | None

Exception чи бібл returns?
Працюємо черзе Exceptions

Без мутування імен:
Погана практика (мутація імені)
data = fetch_data()
data = clean_data(data)
data = transform(data)

Усталена практика
raw_data = fetch_data()
cleaned_data = clean_data(raw_data)
transformed_data = transform(cleaned_data)
