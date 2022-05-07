import requests
import os
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from pathvalidate import sanitize_filename



os.makedirs("books", exist_ok=True)
os.makedirs("images", exist_ok=True)


def get_file_type(url):
    return os.path.splitext(urlparse(url).path)[1]


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError()

def download_txt(book_id, folder='books/'):
    book_url = f'https://tululu.org/txt.php'
    response_loading_book = requests.get(
        book_url,
        params={"id":book_id}
    )
    response_loading_book.raise_for_status()
    try:
        check_for_redirect(response_loading_book)
    except requests.HTTPError:
        pass
    else:
        url = f'https://tululu.org/b{book_id}/'
        response_book_title = requests.get(url)
        response_book_title.raise_for_status()
        title, author, comments, genres, image_url = parse_book_page(response_book_title)
        print(f"Заголовок: {title}")
        print(f"Жанры: {', '.join(genres)}")

        with open(f"{folder}{book_id}. {title}.txt", "w", encoding="UTF-8") as file:
            file.write(response_loading_book.text)

        download_image(book_id, image_url)

def download_image(book_id, image_url, folder="images/"):
    response = requests.get(image_url)
    response.raise_for_status()
    with open(f"{folder}{book_id}.txt", "wb") as file:
        file.write(response.content)


def parse_book_page(html_content):
    soup = BeautifulSoup(html_content.text, 'lxml')

    #Title, author
    title_tag = soup.find("div", id="content").find("h1")
    title, author = title_tag.text.split("::")
    title, author = title.strip(), author.strip()

    #Comments
    try:
        comments_tags = soup.find_all("div", class_="texts")
        comments = list(map(lambda x: x.find("span").text, comments_tags))
    except AttributeError:
        comments = "Нет"
    if not comments:
        comments = "Нет"

    #Genres
    genres_tags = soup.find("span", class_="d_book").find_all("a")
    genres = list(map(lambda x: x.text, genres_tags))

    #Image
    image_tag = soup.find("div", class_="bookimage").find("a").find("img")
    image_url = f'https://tululu.org{image_tag["src"]}'

    return title, author, comments, genres, image_url
    
def main():
    parser = argparse.ArgumentParser(
        description='Скачивание книг и информации о них'
    )
    parser.add_argument('start_id', help='От книги какого id скачивать')
    parser.add_argument('end_id', help='До книги какого id скачивать')
    args = parser.parse_args()
    
    for book_id in range(int(args.start_id), int(args.end_id)):
        filepath = download_txt(book_id)

if __name__ == '__main__':
    main()
