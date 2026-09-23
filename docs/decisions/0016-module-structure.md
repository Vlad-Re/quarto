# 0016. Структура модулів

Статус: прийнято для v1.0.

Рішення: `model.py`, `bot/` (evaluation, random_bot, greedy, minimax), `presenter.py`, `view.py`, `__main__.py`. Типи й правила разом у `model.py`.

Заплановано: розділити `model.py` на `domain.py` і `rules.py`.

Альтернативи: один файл на компонент; папки `core/` і `shell/`.
