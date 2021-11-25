from typing import Optional

from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Path
from fastapi.encoders import jsonable_encoder

from json_database import items, fake_items_db
from schemas import ModelName, Item, UserIn, UserOut
from services import fake_save_user

app = FastAPI()


class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 10):
        self.q = q
        self.skip = skip
        self.limit = limit


async def verify_token(x_token: str = Header(...)):
    if x_token != "fake-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header(...)):
    if x_key != "fake-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


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
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    return commons


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


@app.get("/users/")
async def read_users(commons: CommonQueryParams = Depends()):  # Shortcut
    return commons


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    saved_user = fake_save_user(user)
    return saved_user
