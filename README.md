# Quarto AI

Навчальний проєкт: детермінований ШІ для настільної гри Quarto з простим графічним інтерфейсом для демонстрації.

Статус: у розробці (0.x).

## Запуск (Windows, PowerShell)

```
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m quarto
```

## Структура

- `docs/requirements` — вимоги до програми
- `docs/decisions` — записи ухвалених рішень (ADR)
- `quarto` — код
- `tests` — тести
