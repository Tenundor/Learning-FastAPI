from typing import Optional

from fastapi import Cookie, FastAPI, Header, Path

from schemas import ModelName, Item, UserIn, UserOut

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.put("/items/{item_id}")
async def update_item(
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


@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    return user
