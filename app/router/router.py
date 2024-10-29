import logging
import os

from fastapi import APIRouter, Request, Response

from ..service.data import get_data_from_storage, get_latest_version, upload_folder 
from ..service.model import Trainer

router = APIRouter(
    prefix='/train',
)

metadata = {
    'name': 'Train',
    'description': 'Model Train Service'
}

@router.get("/start")
async def train(model_id: str='10'):
    latest_version = await get_latest_version(model_id=model_id)
    print(f'[INFO] filename: {latest_version}')
    
    get_data_from_storage(object_key=latest_version)

    saved_model_path = Trainer(object_key=latest_version)

    upload_folder(saved_model_path)

@router.get("/test")
async def train(model_id: str='10'):
    latest_version = await get_latest_version(model_id=model_id)
    print(f'[INFO] filename: {latest_version}')
    
    get_data_from_storage(object_key=latest_version)
