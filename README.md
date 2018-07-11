Система комментариев для моделей Python-фреймворка Django. С основным упором - на простоту и беззамороченность функционала.

Создавалась для конкрентых проектов. Вследствии чего на данный момент в коде присутствует некоторое количество кода, завязанного на определенные модели и иные уникальные сущности этих самых проектов. Посему - пока не в PyPy, и больше для личного пользования. Или как шаблон для старта своего форка.

Желающим использовать данный модуль в своих проектах следует, в обязательном порядке, проверять код. Ввиду обозначенных выше привязок.

## Возможности

- Все на Ajax.
- Таски выполняются ассинхронно, через [RQ (Redis Queue)](https://python-rq.org/).

## Зависимости

- [django-rq](https://github.com/rq/django-rq)
- Django >= 2.0
- Python >=3.5 (на других не тестировалось)

## Демо

Демонстрация работы модуля на "живом" сайте - [тут](https://turfront.ru/pub-233#comments).

## Установка

```bash
cd YOUR_PROJECT_DIR
git clone https://github.com/dalay/django-tf-comments comments
```
```python
# settings.php

# Application definition

INSTALLED_APPS = [
    ...,
    'comments',
]
```
```bash
./manage.py migrate
```
## Использование (в шаблоне)
```pyton
# some model template file
...
{% load comments_tags %}
...
{% get_comments SOME_MODEL_OBJECT %}
```
