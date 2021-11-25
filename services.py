from json_database import fake_users_db
from schemas import UserIn, UserInDb, UserOut


def fake_password_hasher(raw_password: str):
    return "fakehashed" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDb(**user_in.dict(), hashed_password=hashed_password)
    print('User saved... not realy')
    return user_in_db


def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserOut(**user_dict)
