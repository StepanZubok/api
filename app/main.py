from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import Base
from .database import engine
from .routers import posts, users, votes
from . import auth

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://192.168.1.250:3000",
    "http://192.168.1.83:3000",
    "http://192.168.1.250",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)  # Only include once!
app.include_router(votes.router)


@app.get("/")
def root():
    return {"message": "API is running"}