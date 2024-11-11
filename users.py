from fastapi import APIRouter
from dbconn import DbConn
from users_schemas import UserSchema
from auth_schemas import UserSignUpSchema
from pydantic import EmailStr
from security import hash_password

user_router = APIRouter(tags=['User Get'])


@user_router.get("/all_users")
def get_all_users():
    dbconn = DbConn()

    dbconn.cursor.execute("""SELECT * FROM users""")

    users = dbconn.cursor.fetchall()

    return users


@user_router.get("/{id}")
def get_user_by_id(id):
    dbconn = DbConn()

    dbconn.cursor.execute("""SELECT * FROM users WHERE id=%s""",
                          (id,))
    user = dbconn.cursor.fetchone()

    return user

@user_router.put("/user_id")
def update_user_by_id(user_create_data: UserSchema, id: int):
    dbconn = DbConn()
    try:
        hashed_password = hash_password(user_create_data.password)
    except Exception as err:
        raise err

    try:
        dbconn.cursor.execute("""UPDATE users SET name=%s, email=%s, password=%s WHERE id=%s""",
                              (user_create_data.name, user_create_data.email, hashed_password, id))

        dbconn.conn.commit()
    except Exception as err:
        raise err

    return "User updated"