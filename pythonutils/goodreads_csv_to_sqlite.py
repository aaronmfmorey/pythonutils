#!/usr/bin/env python3
import csv
import os
import re
import requests
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

COVER_IMAGE_DIRECTORY = None
CONTENT_DIRECTORY = None
GOODREADS_DB = None
IMAGE_DOWNLOAD_MAX = 50

GOODREADS_REREAD_STRUCTURE = """
CREATE TABLE goodreads_reread (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	book_id INTEGER NOT NULL,
	date_read TEXT(10) NOT NULL
);
"""

DB_FIELDS = [
    "book_id",
    "title",
    "author",
    "isbn",
    "isbn13",
    "my_rating",
    "date_read",  # Use ISO 8601 format for date
    "my_review",
    "original_publication_year",
]


def run(download_images=False):
    import_file = f"{CONTENT_DIRECTORY}data/goodreads_library_export.csv"
    reader = csv.DictReader(open(import_file))
    image_download_counter = 0

    con = sqlite3.connect(GOODREADS_DB)
    cur = con.cursor()

    print(
        "Creating database table if it doesn't already exist:"
    )  # TODO AMM Convert print to logging
    create_table_if_not_exists(cur)
    print("Database created.")

    for row in reader:
        # Don't get books from other shelves besides "Read"
        if row["Exclusive Shelf"] == "read":
            print("Processing book: ", row["Title"])
            new_row = clean_up_row_data(row)
            download_openlibrary_cover_image(
                new_row, image_download_counter, download_images
            )
            insert_to_goodreads_db(new_row, cur, con)
            print("Finished")


def create_table_if_not_exists(cur):
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS goodreads (
        book_id INTEGER PRIMARY KEY,
        title TEXT,
        author TEXT,
        isbn TEXT,
        isbn13 TEXT,
        my_rating INTEGER,
        date_read TEXT,
        my_review TEXT,
        original_publication_year INTEGER
    )
    """
    )
    # TODO AMM Use DB_FIELDS to build this table statement


def book_already_exists(book_id, cur):
    cur.execute(
        """
            SELECT book_id from goodreads WHERE book_id = ?
        """,
        (book_id,),
    )
    book = cur.fetchone()
    return book is not None


def insert_to_goodreads_db(book, cur, con):
    values = []

    if not book_already_exists(book["book_id"], cur):
        for f in DB_FIELDS:
            values.append(book[f])

        value_string = ", ?" * (len(DB_FIELDS) - 1)
        insert_query = f"""
            INSERT INTO goodreads 
            VALUES (?{value_string})       
        """
        cur.execute(insert_query, values)
        con.commit()

    return cur.execute("SELECT * from goodreads")


def clean_up_row_data(row):
    isbn = row["ISBN"]
    isbn = isbn[2:-1]

    row["isbn"] = isbn
    row.pop("ISBN", None)
    row["isbn13"] = re.sub(r"[^0-9]", "", row["ISBN13"])
    row.pop("ISBN13", None)
    row["url"] = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"

    new_row = {}
    for k, v in row.items():
        better_key = k.lower()
        better_key = better_key.replace(" ", "_")
        new_row[better_key] = v

    if new_row["date_read"] == "":
        new_row["date_read"] = new_row["date_added"]

    new_row["year"] = datetime.strptime(new_row["date_read"], "%Y/%m/%d").strftime("%Y")
    return new_row


def download_openlibrary_cover_image(
    book, image_download_counter, download_images=False
):
    cover_path = f"{COVER_IMAGE_DIRECTORY}{book["isbn"]}.jpg"
    url = f"https://covers.openlibrary.org/b/isbn/{book['isbn']}-M.jpg?default=false"
    if (
        download_images
        and image_download_counter < IMAGE_DOWNLOAD_MAX
        and not os.path.exists(cover_path)
    ):
        print(f"Downloading cover image for book: \"{book['title']}\"")
        image_download_counter += 1
        print(f"Download count: {image_download_counter}/{IMAGE_DOWNLOAD_MAX}")
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0"
            },
        )
        if response.ok:
            cover_file = open(cover_path, "wb")
            cover_file.write(response.content)
            cover_file.close()
        else:
            print(f"Download Failed: {response.status_code} {response.reason}")


if __name__ == "__main__":
    load_dotenv()
    COVER_IMAGE_DIRECTORY = os.getenv("GOODREADS_COVER_IMAGE_DIRECTORY")
    CONTENT_DIRECTORY = os.getenv("CONTENT_DIRECTORY")
    GOODREADS_DB = os.getenv("GOODREADS_DB")
    run(False)
