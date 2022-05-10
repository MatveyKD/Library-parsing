import os
import argparse

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from pathvalidate import sanitize_filename



def get_file_type(url):
    return os.path.splitext(urlparse(url).path)[1]


def check_for_redirect(url):
    response = requests.get(url)
    response.raise_for_status()
    if response.history:
        raise requests.HTTPError()

def download_txt(book_id, filename, folder='books/'):
    book_url = f'https://tululu.org/txt.php'
    response_from_loading_book = requests.get(
        book_url,
        params={"id":book_id}
    )
    response_from_loading_book.raise_for_status()

    with open(folder+filename, "w", encoding="UTF-8") as file:
        file.write(response_from_loading_book.text)


def download_image(book_id, image_url, folder="images/"):
    response = requests.get(image_url)
    response.raise_for_status()
    with open(f"{folder}{book_id}{get_file_type(image_url)}", "wb") as file:
        file.write(response.content)


def parse_book_page(html_content):
    soup = BeautifulSoup(html_content.text, 'lxml')

    a = soup.find("div", id="content")
    print(type(a))
    title_tag = a.find("h1")
    title, author = title_tag.text.split("::")
    title, author = title.strip(), author.strip()

    try:
        comments_tags = soup.find_all("div", class_="texts")
        comments = list(map(lambda x: x.find("span").text, comments_tags))
    except AttributeError:
        comments = []

    genres_tags = soup.find("span", class_="d_book").find_all("a")
    genres = list(map(lambda x: x.text, genres_tags))

    image_tag = soup.find("div", class_="bookimage").find("a").find("img")
    image_url = urljoin('https://tululu.org', image_tag["src"])

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
        default=1,
    )
    parser.add_argument(
        '--end_id',
        help='До книги какого id скачивать',
        default=10
    )
    args = parser.parse_args()
    
    for book_id in range(int(args.start_id), int(args.end_id)):
        print(book_id)
        try:
            check_for_redirect(f'https://tululu.org/txt.php?id={book_id}')
        except requests.HTTPError:
            pass
        else:
            url = f'https://tululu.org/b{book_id}/'
            response_from_book_page = requests.get(url)
            response_from_book_page.raise_for_status()
            book_info = parse_book_page(response_from_book_page)

            filename = f"{book_id}. {book_info['title']}.txt"

            download_txt(book_id, filename)
            download_image(book_id, book_info["image_url"])

if __name__ == '__main__':
    main()
