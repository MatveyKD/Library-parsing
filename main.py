import os
import argparse
import logging
import time

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from pathvalidate import sanitize_filename



def get_file_type(url):
    return os.path.splitext(urlparse(url).path)[1]


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError("Page was redirected to Main library page.")

def download_txt(book_id, filename, folder='books'):
    book_url = f'https://tululu.org/txt.php'
    response = requests.get(
        book_url,
        params={"id":book_id}
    )
    response.raise_for_status()

    with open(os.path.join(folder, filename), "w", encoding="UTF-8") as file:
        file.write(response.text)


def download_image(book_id, image_url, folder="images/"):
    response = requests.get(image_url)
    response.raise_for_status()
    with open(os.path.join(folder, f"{book_id}{get_file_type(image_url)}"), "wb") as file:
        file.write(response.content)


def parse_book_page(url):
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'lxml')

    a = soup.find("div", id="content")
    title_tag = a.find("h1")
    title, author = title_tag.text.split("::")
    title, author = title.strip(), author.strip()

    comments_tags = soup.find_all("div", class_="texts")
    comments = list(map(lambda x: x.find("span").text, comments_tags))

    genres_tags = soup.find("span", class_="d_book").find_all("a")
    genres = list(map(lambda x: x.text, genres_tags))

    image_tag = soup.find("div", class_="bookimage").find("a").find("img")
    image_url = urljoin(url, image_tag["src"])

    return {
        "title": title,
        "author": author,
        "comments": comments,
        "genres": genres,
        "image_url": image_url
    }
    
def main():
    os.makedirs("books", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    
    parser = argparse.ArgumentParser(
        description='Скачивание книг и информации о них'
    )
    parser.add_argument(
        '--start_id',
        help='От книги какого id скачивать',
        type=int,
        default=1,
    )
    parser.add_argument(
        '--end_id',
        help='До книги какого id скачивать',
        type=int,
        default=10
    )
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id):
        while True:
            try:
                url = "https://tululu.org/txt.php"
                response = requests.get(
                    url,
                    params={"id":book_id}
                )
                response.raise_for_status()
                check_for_redirect(response)

                url = f'https://tululu.org/b{book_id}/'
                book_params = parse_book_page(url)

                filename = f"{book_id}. {sanitize_filename(book_params['title'])}.txt"

                download_txt(book_id, filename)
                download_image(book_id, book_params["image_url"])
                break
            except requests.HTTPError as error:
                logging.warning(error)
                break
            except requests.ConnectionError as error:
                logging.error(error)
                time.sleep(3)


if __name__ == '__main__':
    main()
