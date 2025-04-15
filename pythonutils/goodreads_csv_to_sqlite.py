#!/usr/bin/env python3
import csv
import json
import os
import re
import requests
import sqlite3
import subprocess
import sys
from datetime import datetime
from dotenv import load_dotenv

class GoodReadsCsvToSqlite:
    def __init__(self):
        load_dotenv() 
        self.COVER_IMAGE_DIRECTORY = os.getenv("GOODREADS_COVER_IMAGE_DIRECTORY")
        self.CONTENT_DIRECTORY = os.getenv("CONTENT_DIRECTORY")
        self.GOODREADS_DB = os.getenv("GOODREADS_DB")
        self.IMAGE_DOWNLOAD_MAX = 50

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

    def run(self, download_images = False):
        data = []
        importFile = f"{self.CONTENT_DIRECTORY}data/goodreads_library_export.csv"
        outputFile = f"{self.CONTENT_DIRECTORY}data/goodreads.json"
        reader = csv.DictReader(open(importFile))
        image_download_counter = 0

        con = sqlite3.connect(self.GOODREADS_DB)
        cur = con.cursor()

        self.create_table_if_not_exists(cur)

        for row in reader:
            # Don't get books from other shelves besides "Read"
            if row['Exclusive Shelf'] == "read":
                new_row = self.clean_up_row_data(row)
                self.download_openlibrary_cover_image(new_row, image_download_counter, True)
                self.insert_to_goodreads_db(new_row, cur, con)

    def create_table_if_not_exists(cur):
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


    def insert_to_goodreads_db(self, book, cur, con):
        values = []

        if (not self.book_already_exists(book.find('book_id').text, cur)):
            for f in self.DB_FIELDS:
                values.append(book.find(f).text)

            insert_query = '''
                INSERT INTO goodreads 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)       
            '''
            cur.execute(insert_query, values)
            con.commit()
        
        return cur.execute('SELECT * from goodreads')
    
    def clean_up_row_data(row):
        isbn = row["ISBN"]
        isbn = isbn[2:-1]
        row["isbn"] = isbn
        row.pop("ISBN", None)
        row["isbn13"] = re.sub(r"[^0-9]", "", row["ISBN13"])
        row.pop("ISBN13", None)
        row['url'] = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg?default=false"
                
        newRow = {}
        for k, v in row.items():
            betterKey = k.lower()
            betterKey = betterKey.replace(" ", "_")
            newRow[betterKey] = v

        if newRow['date_read'] == "":
            newRow['date_read'] = newRow['date_added']

        newRow['year'] = datetime.strptime(newRow['date_read'], '%Y/%m/%d').strftime('%Y')
        return newRow

    def download_openlibrary_cover_image(self, book, image_download_counter, download_images = False):
        coverPath = f"{self.COVER_IMAGE_DIRECTORY}{book["isbn"]}.jpg"
        url = f"https://covers.openlibrary.org/b/isbn/{book['isbn']}-M.jpg?default=false"
        if download_images and image_download_counter < IMAGE_DOWNLOAD_MAX and not os.path.exists(coverPath):
            image_download_counter += 1
            response = requests.get(
                            url,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0'
                            }
                        )
            if response.ok:
                coverFile = open(coverPath, 'wb')
                coverFile.write(response.content)
                coverFile.close()
            else:
                print(response)

