from http.server import HTTPServer, SimpleHTTPRequestHandler
from livereload import Server

from jinja2 import Environment, FileSystemLoader, select_autoescape
import json


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')


    with open("books_params.json", "r") as file:
        books_params = json.loads(file.read())


    rendered_page = template.render(
        books_params=books_params
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
