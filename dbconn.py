import time

import psycopg2
from fastapi import FastAPI
import uvicorn

from psycopg2.extras import RealDictCursor


class DbConn:
    def __init__(self):
        while True:
            try:
                self.conn = psycopg2.connect(
                    host='localhost',
                    user='postgres',
                    database='fastapiproject',
                    password='password',
                    cursor_factory=RealDictCursor
                )

                self.cursor = self.conn.cursor()

                print("Database connection successfully")
                break
            except Exception as err:
                print(err)
                time.sleep(3)