import datetime

from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException

# import main
# from main import conn, cursor
from dbconn import DbConn
from auth_schemas import UserSignUpSchema, UserLoginSchema
from security import hash_password, verify_password

from jose import jwt, JWTError

from fastapi.security.oauth2 import OAuth2PasswordBearer

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/login')

SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


def get_current_user(token: str = Depends(oauth2_schema)):
    try:
        current_user = verify_token(token)
        return current_user
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="In UserApp/services/auth.py function get_current_user()\n"
                                   "Error occurred while trying to get current user\n"
                                   f"ERR: {err}")


def create_token(user_data: dict):
    token_exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "exp": token_exp,
        "user": user_data
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


def verify_token(token):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers={
            "WWW-Authenticated": 'Bearer'
        }
    )

    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
    except JWTError:
        raise exception

    user_data = payload.get('user')

    return user_data


auth_router = APIRouter(tags=['Auth'])


@auth_router.post("/sign-up")
def sign_up(user_create_data: UserSignUpSchema):
    dbconn = DbConn()
    try:
        hashed_password = hash_password(user_create_data.password)
    except Exception as err:
        raise err

    try:
        dbconn.cursor.execute("""INSERT INTO users
                                (name, email, password) VALUES (%s, %s, %s)""",
                            (user_create_data.name, user_create_data.email, hashed_password))
        dbconn.conn.commit()
    except Exception as err:
        raise err

    return "OK"


@auth_router.post("/login")
def login(login_data: UserLoginSchema):
    dbconn = DbConn()
    try:
        email = login_data.email
        password = login_data.password
    except Exception as err:
        raise err

    try:
        dbconn.cursor.execute("""SELECT * FROM users
                                WHERE email=%s""",
                            (email,))
    except Exception as err:
        raise err

    try:
        user = dbconn.cursor.fetchone()
    except Exception as err:
        raise err

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email '{email}' was not found!"
        )

    user = dict(user)

    if not verify_password(password, user.get('password')):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Wrong password -> '{password}'"
        )

    payload = {
        "user_id": user.get(id),
        "email": user.get(email)
    }

    token = create_token(payload)

    return token