from dotenv import load_dotenv
import json
import os
import requests
import sqlite3
import xmltodict
import xml.etree.ElementTree as ElementTree

def create_table_if_not_exists(con, cur):
    cur.execute('''
    CREATE TABLE IF NOT EXISTS goodreads (
        book_id INTEGER PRIMARY KEY,
        title TEXT,
        author_name TEXT,
        isbn TEXT,
        user_rating INTEGER,
        user_read_at TEXT, -- Use ISO 8601 format for date
        user_review TEXT,
        book_published INTEGER
    )
    ''')

def book_already_exists(book_id, cur):
    cur.execute(
        '''
            SELECT book_id from goodreads WHERE book_id = ?
        ''', 
        (book_id,)
    )
    book = cur.fetchone()
    return book is not None

def insert_to_goodreads_db(book, cur, con):
    values = []

    if (not book_already_exists(book.find('book_id').text, cur)):
        for f in DB_FIELDS:
            values.append(book.find(f).text)

        insert_query = '''
            INSERT INTO goodreads 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)       
        '''
        cur.execute(insert_query, values)
        con.commit()
    
    return cur.execute('SELECT * from goodreads')
    
def download_book_cover(book, cover_image_directory):
    isbn = book.find('isbn').text
    book_cover_image_url = book.find('book_large_image_url').text
    cover_path = f"{cover_image_directory}{isbn}.jpg"
    if not os.path.exists(cover_path):
        print(f"Downloading {book.find('title').text} ({book.find('isbn').text})")
        response = requests.get(
            book_cover_image_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
        )
        if response.ok:
            cover_file = open(cover_path, 'wb')
            cover_file.write(response.content)
            cover_file.close()
        else:
            print("Download failed: " + response.text + " " + str(response.status_code))

download_images = False

load_dotenv()

# TODO AMM move these to a config file
RSS_URL = 'https://www.goodreads.com/review/list_rss/17419152-aaron?page=1&per_page=100&shelf=read'
SQLIITE_DB = '/Users/aaronmorey/Projects/dotcom_astro/src/data/sqlite.db'
COVER_IMAGE_DIRECTORY = os.getenv("GOODREADS_COVER_IMAGE_DIRECTORY")
CONTENT_DIRECTORY = os.getenv("CONTENT_DIRECTORY")
DB_FIELDS = [
    'book_id',
    'title',
    'author_name',
    'isbn',
    'user_rating',
    'user_read_at', # Use ISO 8601 format for date
    'user_review',
    'book_published'
]

# TODO AMM goodreads code from en
image_download_counter = 0
IMAGE_DOWNLOAD_MAX = 50

# with open('./rssoutput.xml', 'r') as file:
#     rss_data = file.read()

rss_data = requests.get(
    RSS_URL, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
)
if rss_data.status_code == 200:
    print(rss_data.text)
else:
    exit(1) # TODO AMM handle error

print(rss_data.text)
# exit(1)

root = ElementTree.fromstring(rss_data.text)
books = root.findall('.//item')

con = sqlite3.connect(SQLIITE_DB)
cur = con.cursor()

create_table_if_not_exists(con, cur)

for b in books:
    new_book = insert_to_goodreads_db(b, cur, con)
    if new_book is not None:
        image_download_counter += 1
        if image_download_counter < IMAGE_DOWNLOAD_MAX and download_images:
            download_book_cover(b, COVER_IMAGE_DIRECTORY);