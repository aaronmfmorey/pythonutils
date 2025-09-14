#!/usr/bin/env python3
import os
import sqlite3
import argparse
from dotenv import load_dotenv


class GoodreadsMetaUpdate:
    def __init__(self):
        load_dotenv()
        self.GOODREADS_DB = os.getenv("GOODREADS_DB")
        self.db_connection = None
        self.db_cursor = None

    def get_arguments(self):
        parser = argparse.ArgumentParser(description="Goodreads Meta Updater")
        parser.add_argument("--book_id", type=int, help="ID of the book to query")
        parser.add_argument(
            "--bookshop_slug", type=str, help="The ISBN number from Bookshop.org"
        )
        parser.add_argument(
            "--no_bookshop",
            type=bool,
            help="The indicator that there is no Bookshop.org reference for this book",
        )
        args = parser.parse_args()
        return args

    def get_db_connection(self):
        if self.db_connection is None:
            con = sqlite3.connect(self.GOODREADS_DB)
            self.db_connection = con
            self.db_cursor = con.cursor()

        return self.db_connection, self.db_cursor

    def get_book_meta_by_book_id(self, book_id):
        conn, cursor = self.get_db_connection()
        cursor.execute(
            """
                SELECT * from goodreads_meta WHERE book_id = ?
            """,
            (book_id,),
        )
        return cursor.fetchone()

    def insert_book_meta(self, args):
        conn, cursor = self.get_db_connection()
        result = cursor.execute(
            """
                insert into goodreads_meta (
                    book_id, 
                    bookshop_slug, 
                    no_bookshop
                ) values (
                    ?, 
                    ?, 
                    ?
                )
            """,
            (args.book_id, args.bookshop_slug, args.no_bookshop),
        )
        conn.commit()
        return result

    def update_book_meta(self, args):
        conn, cursor = self.get_db_connection()
        result = cursor.execute(
            """
                update goodreads_meta
                set book_id = ?,
                    bookshop_slug = ?,
                    no_bookshop = ?
                where book_id = ?
            """,
            (args.book_id, args.bookshop_slug, args.no_bookshop, args.book_id),
        )
        conn.commit()
        return result

    def upsert_goodreads_meta(self, args):
        book_meta = self.get_book_meta_by_book_id(args.book_id)
        if book_meta is None:
            self.insert_book_meta(args)
        else:
            self.update_book_meta(args)

    def main(self):
        args = self.get_arguments()
        if args.book_id is None or (
            args.bookshop_slug is None and args.no_bookshop is None
        ):
            raise ValueError(
                "Book ID and at least one of bookshop_slug and no_bookshop is non-empty."
            )

        # cur = self.get_db_connection()
        self.upsert_goodreads_meta(args)


if __name__ == "__main__":
    grm = GoodreadsMetaUpdate()
    grm.main()
