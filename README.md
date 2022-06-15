# Library-parsing
Парсим онлайн-библиотеку [tululu](https://tululu.org/) с помощью Python.

## Как установить
Python3 должен быть установлен. Далее загрузите ряд зависимостей с помощью pip (pip3):

    pip install -r requirements.txt

## Агрументы

Скрипт принимает на вход 5 агрументов:

`start_page` - С какой страницы скачивать, число.

`end_page` - До какой страницы скачивать, число.

`skip_img` - Пропускать ли скачивание картинок книг, булево значение.

`skip_txt` - Пропускать ли скачивание книг, булево значение.

`json_path` - Путь к `.json` файлу результатами, строка. По умолчанию `books_params.json`.

`dest_fold` - Путь до папки с результатами: книгами, картинками и JSON. По умолчанию изначальная дирекория.

`del_old` - Удалять ли уже скаченные книги.


При запуске необходимо передать их:

    C:\Users\hp\Books>main.py --start_page 10 --end_page 20 --skip_img --json_path results.json


## Сайт

Сайт библиотеки опубликован и открыт: [https://matveykd.github.io/Library-parsing/pages/index1.html](https://matveykd.github.io/Library-parsing/pages/index1.html)

## Пример успешного запуска скрипта
При успешном запуске скрипта у вас должны появится папка *"books"* с текстовыми файлами книг и папка *"images"* с обложками книг.
Скрипт нечего не выводит.

    C:\Users\hp\Books>main.py

    C:\Users\hp\Books>
