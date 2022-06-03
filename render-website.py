from http.server import HTTPServer, SimpleHTTPRequestHandler
from livereload import Server

from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from more_itertools import chunked


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')


    with open("books_params.json", "r") as file:
        books_params = json.loads(file.read())

    print(list(chunked(books_params, 2))[1])
    rendered_page = template.render(
        books_params=list(chunked(books_params, 2))
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

on_reload()

server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
