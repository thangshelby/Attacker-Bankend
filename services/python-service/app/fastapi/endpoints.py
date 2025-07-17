import pickle
import os
from fastapi import APIRouter
from app.core.service import say_hello
from app.core.predict import predict as model_predict
import json 
from pydantic import BaseModel
router = APIRouter()

@router.get("/hello")
def hello():
    name="thang"
    return say_hello(name)


class predictDataRequest(BaseModel):
    features: list  

@router.post("/predict")
def predict(data: predictDataRequest):
    print(data)
    return model_predict(data.features)

