from http.server import HTTPServer, SimpleHTTPRequestHandler
from livereload import Server

from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from more_itertools import chunked
from math import ceil

def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')


    with open("books_params.json", "r", encoding="UTF8") as file:
        books_params = json.load(file)


    per_column = 10
    per_line = 2
    per_page = per_column * per_line
    chunked_books = list(chunked(list(chunked(books_params, per_line)), per_column))

    for index, books in enumerate(chunked_books, start=1):
        rendered_page = template.render(
            books_params=books,
            all_pages=ceil(len(books_params) / per_page),
            cur_page=index
        )

        with open(f'pages/index{index}.html', 'w', encoding="UTF-8") as file:
            file.write(rendered_page)

on_reload()

server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
