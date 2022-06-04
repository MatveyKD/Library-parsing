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


    with open("books_params.json", "r") as file:
        books_params = json.loads(file.read())

    chunked_books = list(chunked(list(chunked(books_params, 2)), 10))

    for index, books in enumerate(chunked_books):
        rendered_page = template.render(
            books_params=books,
            all_pages=ceil(len(books_params) / 20),
            cur_page=index+1
        )

        with open(f'pages/index{index+1}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)

on_reload()

server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
