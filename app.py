import re
import jwt 
import datetime

from functools import wraps

from fastapi import (
    FastAPI,
    HTTPException,
    Header,
    Depends
)

from pydantic import (
    BaseModel,
    validator
)

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="FastAPI", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    email: str
    password: str

    @validator("email")
    def email_regex(cls, v):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if not re.fullmatch(regex, v):
            raise ValueError("Invalid email")
        return v

    @validator("password")
    def password_hash_checker(cls, v):
        regex = r"^[a-fA-F0-9]{64}$"
        if not re.fullmatch(regex, v):
            raise ValueError("Invaid password hash")
        return v


@app.get("/")
async def index_event():
    return {"Hello": "World!"}

users = []

@app.post("/signup")
async def signup(user: User):
    if user.dict() in users:
        raise HTTPException(status_code=403, detail="User already exist")
    
    users.append(user.dict())

    jwt_token = jwt.encode({
        "email": user.dict()["email"],
        "expire": (datetime.datetime.now() + datetime.timedelta(days=30)).timestamp()
    }, "SUPERSECRETKEY", algorithm="HS256")

    return {"token": jwt_token}


@app.post("/signin")
async def signin(user: User):
    if user.dict() not in users:
        raise HTTPException(status_code=404, detail="User not found or password is invalid")
    
    # REPLACE THIS SHIT..
    for usr in users:
        if user.dict() == usr:
            jwt_token = jwt.encode({
                "email": user.dict()["email"],
                "expire": (datetime.datetime.now() + datetime.timedelta(days=30)).timestamp()
            }, "SUPERSECRETKEY", algorithm="HS256")

            return {"token": jwt_token}


async def login_required(Authorization=Header("Authorization")):
    try:
        if Authorization == "Authorization":
            raise
        jwt_token = jwt.decode(Authorization, "SUPERSECRETKEY", algorithms=["HS256"])
    except:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/secure", dependencies=[Depends(login_required)])
async def secure_page():
    return {"message": "Welcome on secure page!"}