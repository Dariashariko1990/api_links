# Web-приложение для простого учета посещенных ссылок
Приложение предоставляет два HTTP ресурса:  
1. Публикация списка посещенных ссылок

POST /visited_links 

Пример тела запроса:
```
{
   "links": [
      "https://ya.ru",
      "https://ya.ru?q=123",
      "funbox.ru", "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
   ] 
}
```
Пример ответа на запрос:
```
{
    "status": "ok"
}
```

2. Получение списка уникальных посещенных доменов за период времени

GET /visited_domains?from=1545221231&to=1545217638

Пример ответа на запрос:
```
{
    "domains": [
       "ya.ru", 
       "funbox.ru", 
       "stackoverflow.com"
    ],
    "status": "ok"
}
```
#### Документация по проекту
Для запуска проекта необходимо:  
Установить зависимости:
```
pip install -r requirements.txt
```
Выполнить команду:
```
python manage.py runserver
```
