import logging
import os

from fastapi import APIRouter, Request, Response

from ..service.data import  get_latest_version, download_from_s3
from ..service.chatgpt_tuning import make_tuning_dataset, start_training
from ..service.elevenlabs_tuning import add_voice
# from ..service.model import Trainer

router = APIRouter(
    prefix='/train',
)

metadata = {
    'name': 'Train',
    'description': 'Model Train Service'
}

# chatgpt fine-tuning
# @router.get('/start/text', tags=['Train'])
async def text_train(model_id: str):
    print('[INFO] ROUTER text_train')

    latest_version = await get_latest_version(model_id, True)
    downloaded_path = await download_from_s3(latest_version, True)
    print(f'[INFO] ROUTER text_train - latest_version: {latest_version}')

    dataset_id = await make_tuning_dataset(downloaded_path)
    print(f'[INFO] ROUTER text_train - dataset_id: {dataset_id}')

    gpt_id = await start_training(dataset_id)
    print(f'[INFO] ROUTER text_train - gpt_id: {gpt_id}')

    return gpt_id

@router.get('/start/voice', tags=['Train'])
async def voice_train(model_id: str):
    print('[INFO] ROUTER voice_train')

    latest_version = await get_latest_version(model_id, False)
    downloaded_path = await download_from_s3(latest_version, False)
    print(f'[INFO] ROUTER voice_train - latest_version: {latest_version}')

    voice_id = await add_voice(latest_version, downloaded_path)
    print(f'[INFO] ROUTER voice_train - voice_id: {voice_id}')

    return voice_id
    


# # QLoRa
# @router.get("/start")
# async def train(model_id: str):
#     latest_version = await get_latest_version(model_id=model_id)
#     print(f'[INFO] filename: {latest_version}')
    
#     get_data_from_storage(object_key=latest_version)

#     saved_model_path = Trainer(object_key=latest_version)

#     upload_folder(saved_model_path)