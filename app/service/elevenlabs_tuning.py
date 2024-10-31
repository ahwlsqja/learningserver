import os
import requests

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ELEVENLABS_API_KEY')

async def add_voice(model_name: str, audio_file_path: str):
    base_url = 'https://api.elevenlabs.io/v1/voices/add'

    headers = {'xi-api-key': api_key}
    files = [('files', open(audio_file_path, 'rb'))]

    data = {
        'name': model_name,
        'remove_background_noise': 'true',
    }

    response = requests.post(base_url, headers=headers, files=files, data=data)

    voice_id = response.json()['voice_id']

    return voice_id