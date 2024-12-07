import pandas as pd
from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel


class Post(BaseModel):
    title: str
    content: str


class UpdatedPost(BaseModel):
    title: str | None = None
    content: str | None = None


app = FastAPI()


posts = pd.DataFrame([
    {
        "title": "This is the default title",
        "content": "This is the default content",
    }
])

posts.index.name = "id"


@app.get("/")
def root():

    return {"message" : "Hello World!"}


@app.get("/posts/")
def get_posts():

    return posts.reset_index().to_dict("records")


# This function must be placed before `get_post`
@app.get("/posts/latest")
def get_post_latest():
    post = posts.iloc[-1]

    return post.to_dict()


@app.get("/posts/{id}")
def get_post(id: int):
    try:
        post = posts.loc[id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no post with id {id}"
        )
    
    return post.to_dict()


@app.post("/posts/", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    post = pd.Series(post.model_dump())
    posts.loc[posts.index[-1] + 1] = post

    return post.to_dict()


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    try:
        posts.drop(index=id, inplace=True)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no post with id {id}"
        )


@app.put("/posts/{id}")
def update_post(id: int, post: UpdatedPost):
    if id not in posts.index:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There is no post with id {id}"
        )

    post = pd.Series(post.model_dump())
    posts.loc[id, post.notna()] = post[post.notna()]
    
    if post.isna().all():
        return {"message": f"No information to update for post with id {id}"}
    else:
        return {"message": f"Post {id} is updated"}
    