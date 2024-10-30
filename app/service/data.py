import os

from datasets import Dataset
import logging
import pandas as pd

from .. import S3_CLIENT, AWS_S3_BUCKET_NAME



# # QLoRa
# def get_data_from_storage(object_key: str) -> None:
#     json_data = S3_CLIENT.download_file(AWS_S3_BUCKET_NAME, object_key, f"./{object_key}")
#     # print(f'json_data: {json_data}')
#     # print(f'json_data type: {type(json_data)}')

#     conversations = json_data['conversations']
#     instruction = conversations['instruction']
#     output = conversations['output']

#     dataset_df = pd.DataFrame({
#         "instruction": instruction,
#         "output": output
#     })
#     dataset_custom = Dataset.from_pandas(dataset_df)

#     dataset_custom.save_to_disk("dataset/dataset")
#     logging.info('Dataset Saved in dataset/dataset')

# def upload_folder(folder: str, local_folder_path: str):
#     try:
#         curr_dir = os.path.dirname(os.path.realpath(__file__))
#         local_folder_path = os.path.join(curr_dir, local_folder_path)
        
#         for filename in os.listdir(local_folder_path):
#             file_path = os.path.join(local_folder_path, filename)
#             if os.path.isfile(file_path):
#                 s3_file_path = f"{folder}/{filename}"
#                 with open(file_path, "rb") as file_data:
#                     S3_CLIENT.upload_fileobj(file_data, AWS_S3_BUCKET_NAME, s3_file_path)

#         os.system(f'rm -r {local_folder_path}')

#         return {"info": f"Files uploaded to '{folder}' in S3."}

#     except Exception as e:
#         return {"error": str(e)}

# async def get_latest_version(model_id: str) -> str:
#     try:
#         response = S3_CLIENT.list_objects_v2(Bucket=AWS_S3_BUCKET_NAME, Prefix=str(model_id))
#         if 'Contents' not in response:
#             return None
        
#         files = [obj['Key'] for obj in response['Contents']]
#         latest_file = max(files, key=lambda x: int(x.split('_')[-1].split('.')[0]))

#         return latest_file
    
#     except Exception as e:
#         return f"Error: {e}"
