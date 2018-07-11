Система комментариев для моделей Python-фреймворка Django. Разработана с нуля, как самостоятельная библиотека. Без использования "родных" джанговских комментариев. С основным упором - на простоту, малое потребление ресурсов сервера и беззамороченность функционала.

Создавалось под конкретные проекты. Вследствии чего возможно присутствие в коде остаточных вкраплений. Посему - пока не в PyPy, а больше для личного пользования. 

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
# settings.py

# Application definition

INSTALLED_APPS = [
    ...,
    'comments',
]
...

COMMENTS_ON_PAGE = 20 # по-умолчанию, если не указывать,
                      # выводится 10 комментариев (с пейджером, если их больше) 
```
```bash
./manage.py migrate
```
## Использование (в шаблоне)
```html
# some model template file
...
{% load comments_tags %}
...
{% get_comments SOME_MODEL_OBJECT %} <!-- комментарии к объекту -->
...
{% comments_count SOME_MODEL_OBJECT %} <!-- количество комментариев к объекту -->
...
<!-- 
Вывод списка последних комментариев.
Необязательные аргументы:
LIMIT - INT, колличество выводимых ком-ев;
SOME_MODEL_OBJECT - OBJ, если указать - выведет последние к определенному объекту -->
{% latest_comments LIMIT SOME_MODEL_OBJECT %}
...
{% last_comment_datetime SOME_MODEL_OBJECT %} <!-- дата/время последнего комментария -->
```
## Сигналы
#### comment_added_onmoderate
Появление нового неопубликованного комментария.
#### comment_updated
Пока не используется, только объявлен.)
