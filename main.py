from fastapi import FastAPI
import psycopg2
import uvicorn
from psycopg2.extras import RealDictCursor
import time

from models import Base
from database import engine
from auth import auth_router
from users import user_router


Base.metadata.create_all(bind=engine)

while True:
    try:
        conn = psycopg2.connect(
            host='localhost',
            user='postgres',
            database='fastapiproject',
            password='password',
            cursor_factory=RealDictCursor
        )

        cursor = conn.cursor()
        break
    except Exception as err:
        print(err)
        time.sleep(3)

app = FastAPI()

@app.get("/")
def get_main():
    return "Hello"


app.include_router(auth_router)
app.include_router(user_router)


if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)