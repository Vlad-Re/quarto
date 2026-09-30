# Quarto AI

Проєкт: детермінований ШІ для настільної гри Quarto з простим графічним інтерфейсом для демонстрації.

Статус: у розробці (0.x).

## Запуск (Windows, PowerShell)

```
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m quarto
```

Усі команди нижче виконуються з кореня проєкту з активованим venv.

## Тести (pytest)

Налаштування — у `pyproject.toml`, тести лежать у `tests/`.

```
pytest                                # усі тести
pytest -q                             # коротший вивід
pytest tests/test_minimax.py          # один файл
pytest -k same_move                   # тести, в назві яких є "same_move"
pytest -x                             # зупинитися на першому падінні
```

## Лінтер і форматер (Ruff)

```
ruff check .          # знайти проблеми
ruff check . --fix    # виправити те, що можна автоматично (напр. порядок імпортів)
ruff format .         # відформатувати код
```

## Перевірка типів (Pyright, strict)

У VS Code Pylance перевіряє типи під час набору. З терміналу:

```
pyright
```

Pyright читає налаштування з `pyproject.toml` і сам знаходить `.venv`.

# Бенчмарк
```
python -m tools.bench_depth
python -m tools.bench_depth --limit 10
```

## Перед комітом

```
ruff format .
ruff check .
pyright
pytest -q
```

## Налаштування гри

Параметри, які часто змінюються (активний бот, затримка ходу, глибина мінімаксу, вага загрози в оцінці), зібрані в `quarto/config.py`.

## Структура

- `docs/requirements` — вимоги до програми
- `docs/decisions` — записи ухвалених рішень (ADR)
- `quarto` — код
- `tests` — тести
