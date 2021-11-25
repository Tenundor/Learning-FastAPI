from typing import Optional

from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Path
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from json_database import items, fake_items_db, fake_users_db
from schemas import ModelName, Item, UserIn, UserOut, UserInDb
from services import fake_save_user, fake_decode_token, fake_password_hasher

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 10):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDb(**user_dict)
    hashed_password = fake_password_hasher(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


async def verify_token(x_token: str = Header(...)):
    if x_token != "fake-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header(...)):
    if x_key != "fake-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


async def get_current_active_user(current_user: UserOut = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.put("/items/{item_id}")
async def replace_item(
        *,
        item_id: int = Path(..., title="The ID of the item to get", ge=0, le=1000),
        q: Optional[str] = None,
        item: Optional[Item] = None,
        ads_id: Optional[str] = Cookie(None),
        user_agent: Optional[str] = Header(None),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    if ads_id:
        results.update({"ads_id": ads_id})
    if user_agent:
        results.update({"user_agent": user_agent})
    return results


@app.patch("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    stored_item_data = items[item_id]
    stored_item_model = Item(**stored_item_data)
    update_data = item.dict(exclude_unset=True)
    updated_item = stored_item_model.copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item


@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams),
                     token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
        user_id: int, item_id: str, q: str = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "Это удивительная позиция, имеющая длинное описание"}
        )
    return item


@app.get("/users/me")
async def read_users_me(current_user: UserOut = Depends(get_current_active_user)):
    return current_user


@app.get("/users/")
async def read_users(commons: CommonQueryParams = Depends()):  # Shortcut
    return commons


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    saved_user = fake_save_user(user)
    return saved_user
