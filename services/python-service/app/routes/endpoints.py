import pickle
import os
from fastapi import APIRouter
from app.core.service import say_hello
import json 
from pydantic import BaseModel
router = APIRouter()

@router.get("/hello")
def hello():
    name="thang"
    return say_hello(name)


class predictDataRequest(BaseModel):
    features: list  
