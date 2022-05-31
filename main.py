import os
import argparse
import logging
import time
import json

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from pathvalidate import sanitize_filename



def get_file_type(url):
    return os.path.splitext(urlparse(url).path)[1]


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError("Page was redirected to Main library page.")

def download_txt(txt_url, filename, folder='books/'):
    response = requests.get(txt_url)
    response.raise_for_status()
    check_for_redirect(response)

    path = os.path.join(folder, filename)
    with open(path, "w", encoding="UTF-8") as file:
        file.write(response.text)
    return path


def download_image(book_id, image_url, folder="images/"):
    response = requests.get(image_url)
    response.raise_for_status()
    path = os.path.join(folder, f"{book_id}{get_file_type(image_url)}")
    with open(path, "wb") as file:
        file.write(response.content)
    return path


def parse_book_page(url, response):    
    soup = BeautifulSoup(response.text, 'lxml')

    title_tag = soup.select_one("h1")
    title, author = title_tag.text.split("::")
    title, author = title.strip(), author.strip()

    comments_tags = soup.select(".texts span")
    comments = list(map(lambda x: x.text, comments_tags))

    genres_tags = soup.select("span.d_book a")
    genres = list(map(lambda x: x.text, genres_tags))

    image_tag = soup.select_one(".bookimage a img")
    image_url = urljoin(url, image_tag["src"])

    txt_tag = soup.select_one('[title*="скачать книгу txt"]')
    txt_url = urljoin(url, txt_tag["href"])


    return {
        "title": title,
        "author": author,
        "comments": comments,
        "genres": genres,
        "image_url": image_url,
        "txt_url": txt_url
    }

def del_old(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            os.remove(file_path)

def add_args():
    parser = argparse.ArgumentParser(
        description='Скачивание книг и информации о них'
    )
    parser.add_argument(
        '--start_page', help='С какой страницы скачивать',
        type=int, default=1,
    )
    parser.add_argument(
        '--end_page', help='До какой страницы скачивать',
        type=int, default=0
    )
    parser.add_argument(
        '--skip_img', help='Пропускать ли скачивание картинок книг',
        action='store_true',
    )
    parser.add_argument(
        '--skip_txt', help='Пропускать ли скачивание книг',
        action='store_true',
    )
    parser.add_argument(
        '--json_path', help='Путь к .json файлу с результатами',
        default="books_params.json"
    )
    parser.add_argument(
        '--dest_fold', help='Путь к папке с книгами, картинками и JSON',
        default=""
    )
    parser.add_argument(
        '--del_old', help='Удалять ли давно скаченные книги',
        action='store_true',
    )
    args = parser.parse_args()

    return args

def main():
    args = add_args()

    books_folder = os.path.join(args.dest_fold, "books")
    img_folder = os.path.join(args.dest_fold, "images")
    os.makedirs(books_folder, exist_ok=True)
    os.makedirs(img_folder, exist_ok=True)
    
    if args.del_old:
        del_old(books_folder)
        del_old(img_folder)

    book_id = 0
    books_params = []
    if args.end_page == 0:
        args.end_page = args.start_page+1
    for page in range(args.start_page, args.end_page):
        while True:
            try:
                response = requests.get(f"https://tululu.org/l55/{page}")
                response.raise_for_status()
                check_for_redirect(response)

                soup = BeautifulSoup(response.text, 'lxml')
                books_tags = soup.select(".d_book")
                for book_tag in books_tags:
                    try:
                        book_href = book_tag.select_one("a")["href"]
                        book_url = urljoin("https://tululu.org", book_href)
           
                        response = requests.get(book_url)
                        response.raise_for_status()
                        check_for_redirect(response)
                        book_params = parse_book_page(book_url, response)
                        txt_url = book_params["txt_url"]

                        book_filename = f"{book_id}. {sanitize_filename(book_params['title'])}.txt"

                        if not args.skip_txt:
                            book_path = download_txt(txt_url, book_filename, books_folder)
                        else: book_path = None
                        if not args.skip_img:
                            image_path = download_image(book_id, book_params["image_url"], img_folder)
                        else: image_path = None
                            
                        books_params.append({
                            "title": book_params["title"],
                            "author": book_params["author"],
                            "image_path": image_path,
                            "book_path": book_path,
                            "comments": book_params["comments"],
                            "genres": book_params["genres"],
                        })
                            
                        book_id += 1
                    except requests.HTTPError as error:
                        logging.warning(error)
                        break
                    except TypeError:
                        logging.warning("Book hasn't url for loading")
                    except requests.ConnectionError as error:
                        logging.error(error)
                        time.sleep(3)
                break
            except requests.HTTPError as error:
                logging.warning(error)
                break
            except requests.ConnectionError as error:
                logging.error(error)
                time.sleep(3)

    with open(os.path.join(args.dest_fold, args.json_path), "w") as file:
        file.write(json.dumps(books_params, ensure_ascii=False))


if __name__ == '__main__':
    main()
