#!/usr/bin/env python3
import csv
import json
import os
import re
import requests
import subprocess
import sys
from datetime import datetime
from dotenv import load_dotenv

class GoodReadsCsvToJson:
    def __init__(self):
        pass

    @staticmethod
    def run(download_images = False):
        load_dotenv() 
        COVER_IMAGE_DIRECTORY = os.getenv("GOODREADS_COVER_IMAGE_DIRECTORY")
        CONTENT_DIRECTORY = os.getenv("CONTENT_DIRECTORY")
        data = []
        importFile = f"{CONTENT_DIRECTORY}data/goodreads_library_export.csv"
        outputFile = f"{CONTENT_DIRECTORY}data/goodreads.json"
        reader = csv.DictReader(open(importFile))

        imageDownloadCounter = 0
        IMAGE_DOWNLOAD_MAX = 50

        for row in reader:
            if row['Exclusive Shelf'] == "read":
                # row.pop("ISBN", None)
                isbn = row["ISBN"]
                isbn = isbn[2:-1]
                row["isbn"] = isbn
                row.pop("ISBN", None)
                row["isbn13"] = re.sub(r"[^0-9]", "", row["ISBN13"])
                row.pop("ISBN13", None)
                url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg?default=false"
                coverPath = f"{COVER_IMAGE_DIRECTORY}{isbn}.jpg"
                if download_images and imageDownloadCounter < IMAGE_DOWNLOAD_MAX and not os.path.exists(coverPath):
                    imageDownloadCounter += 1
                    response = requests.get(url)
                    if response.ok:
                        coverFile = open(coverPath, 'wb')
                        coverFile.write(response.content)
                        coverFile.close()
                    else:
                        print(response)

                newRow = {}
                for k, v in row.items():
                    betterKey = k.lower()
                    betterKey = betterKey.replace(" ", "_")
                    newRow[betterKey] = v

                if newRow['date_read'] == "":
                    newRow['date_read'] = newRow['date_added']

                newRow['year'] = datetime.strptime(newRow['date_read'], '%Y/%m/%d').strftime('%Y')
                data.append(newRow);
        sortedJson = sorted(data, key=lambda d: d['date_read'], reverse=True)
        jsonString = json.dumps(sortedJson, indent=2,)

        try:
            os.remove(outputFile)
        except OSError:
            pass

        with open(outputFile, "w") as text_file:
            text_file.write(jsonString)


if __name__ == "__main__":
    GoodReadsCsvToJson().run(True)