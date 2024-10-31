import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=openai_api_key)

async def make_tuning_dataset(downloaded_path: str) -> str:
    uploaded_dataset = client.files.create(
        file=open(downloaded_path, 'rb'),
        purpose='fine-tune'
    )

    dataset_id = uploaded_dataset.id

    return dataset_id

async def start_training(dataset_id: str):
    print(f'[INFO] EXECUTE start_training()')

    training_detail = client.fine_tuning.jobs.create(
        training_file=dataset_id,
        model='gpt-4o-mini-2024-07-18'
    )

    training_id = training_detail.id
    print(f'[INFO] EXECUTE start_training() - training_id: {training_id}')
    time.sleep(5)

    while True:
        message = client.fine_tuning.jobs.list_events(fine_tuning_job_id=training_id, limit=1).data[0].message
        print(f'[INFO] EXECUTE start_training() - message: {message}')

        if message == 'The job has successfully completed': break
        else: time.sleep(60)

    for job in client.fine_tuning.jobs.list():
        if job.id == training_detail.id:
            gpt_id = job.fine_tuned_model

    return gpt_id