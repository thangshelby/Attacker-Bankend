from fastapi import APIRouter
from app.core.service import say_hello

router = APIRouter()

@router.get("/hello")
def hello():
    name="thang"
    return say_hello(name)
