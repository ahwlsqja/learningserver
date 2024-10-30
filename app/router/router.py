import logging
import os

from fastapi import APIRouter, Request, Response

from ..service.data import get_data_from_storage, get_latest_version, upload_folder, download_from_s3
from ..service.chatgpt_tuning import make_tuning_dataset, start_training
# from ..service.model import Trainer

router = APIRouter(
    prefix='/train',
)

metadata = {
    'name': 'Train',
    'description': 'Model Train Service'
}

# chatgpt fine-tuning
@router.get('/start', tags=['Train'])
async def train(model_id: str):
    print('[INFO] ROUTER train')
    latest_version = await get_latest_version(model_id)
    downloaded_path = await download_from_s3(latest_version)
    print(f'[INFO] ROUTER train - latest_version: {latest_version}')

    dataset_id = await make_tuning_dataset(downloaded_path)
    print(f'[INFO] ROUTER train - dataset_id: {dataset_id}')

    gpt_id = await start_training(dataset_id)
    print(f'[INFO] ROUTER train - gpt_id: {gpt_id}')

    return gpt_id

# # QLoRa
# @router.get("/start")
# async def train(model_id: str):
#     latest_version = await get_latest_version(model_id=model_id)
#     print(f'[INFO] filename: {latest_version}')
    
#     get_data_from_storage(object_key=latest_version)

#     saved_model_path = Trainer(object_key=latest_version)

#     upload_folder(saved_model_path)
