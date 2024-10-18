from fastapi import FastAPI
from fastapi.params import Path

app = FastAPI()






@app.get("/user/{username}/{age}")
async def login(username: str = Path(min_length=3, max_length=15, description='Enter your username', example='Ilya'),
                age: int = Path(ge=0, le=100, description="Enter your age")) -> dict:
    return {"user": username, "age": age}

@app.get("/")
async def welcome() -> dict:
    return {"message": "Hello World"}
'''
@app.get("/user/profile")
async def profile() -> dict:
    return {"profile": "View profile user"}

@app.get("/user/{user}")
async def user(user: str) -> dict:
    return {"user": f'Hello {user}'}'''

