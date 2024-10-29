import torch
import transformers
from datasets import load_from_disk
from transformers import (
    BitsAndBytesConfig,
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TextStreamer,
    pipeline
)
from peft import (
    LoraConfig,
    prepare_model_for_kbit_training,
    get_peft_model,
    get_peft_model_state_dict,
    set_peft_model_state_dict,
    TaskType,
    PeftModel
)
from trl import SFTTrainer
import os
import json
import torch
import transformers
import pandas as pd
from datasets import load_dataset, Dataset, concatenate_datasets
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

class Trainer:
    def __init__(self, object_key: str) -> str:
        base_model_name = "MLP-KTLim/llama-3-Korean-Bllossom-8B"
        dataset_path = "dataset/dataset"

        self.save_model_path = object_key

        # NF4 양자화를 위한 설정
        self.nf4_config = BitsAndBytesConfig(
            # load_in_4bit=True, # 모델을 4비트 정밀도로 로드
            load_in_8bit=True, # 모델 학습 시간 및 gpu 자원 제한으로 8비트 로드
            bnb_4bit_quant_type="nf4", # 4비트 NormalFloat 양자화: 양자화된 파라미터의 분포 범위를 정규분포 내로 억제하여 정밀도 저하 방지
            bnb_4bit_use_double_quant=True, # 이중 양자화: 양자화를 적용하는 정수에 대해서도 양자화 적용
            bnb_4bit_compute_dtype=torch.bfloat16 # 연산 속도를 높이기 위해 사용 (default: torch.float32)
        )

        self.lora_config = LoraConfig(
            r=4, # LoRA 가중치 행렬의 rank. 정수형이며 값이 작을수록 trainable parameter가 적어짐
            lora_alpha=8, # LoRA 스케일링 팩터. 추론 시 PLM weight와 합칠 때 LoRA weight의 스케일을 일정하게 유지하기 위해 사용
            lora_dropout=0.05,
            target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'], # LoRA를 적용할 layer. 모델 아키텍처에 따라 달라짐
            bias='none', # bias 파라미터를 학습시킬지 지정. ['none', 'all', 'lora_only']
            task_type=TaskType.CAUSAL_LM
        )

        logging.info('[INFO] Trainer: Loading Model and Tokenizer')
        self.base_model, self.tokenizer = self.load_model_n_tokenizer(base_model_name)
        logging.info('[INFO] Trainer: Done Loading Model and Tokenizer')

        dataset = load_from_disk(dataset_path)

        remove_column_keys = dataset.features.keys()
        dataset_cvted = dataset.shuffle().map(self.generate_prompt, remove_columns=remove_column_keys)

        remove_column_keys = dataset_cvted.features.keys()
        dataset_tokenized = dataset_cvted.map(self.tokenize_function, batched=True, remove_columns=remove_column_keys)

        # 양자화된 모델을 학습하기 전, 전처리를 위해 호출
        model = prepare_model_for_kbit_training(self.base_model)
        # LoRA 학습을 위해서는 아래와 같이 peft를 사용하여 모델을 wrapping 해주어야 함
        self.model = get_peft_model(model, self.lora_config)

        self.train_args = transformers.TrainingArguments(
            per_device_train_batch_size=2, # 각 디바이스당 배치 사이즈. 작을수록(1~2) 좀 더 빠르게 alignment 됨
            gradient_accumulation_steps=4, 
            warmup_steps=1,
            #num_train_epochs=1,
            max_steps=1000, 
            learning_rate=2e-4, # 학습률
            bf16=True, # bf16 사용 (지원되는 하드웨어 확인 필요)
            output_dir="outputs",
            optim="paged_adamw_8bit", # 8비트 AdamW 옵티마이저
            logging_steps=50, # 로깅 빈도
            save_total_limit=3 # 저장할 체크포인트의 최대 수
        )

        self.trainer = SFTTrainer(
            model=model,
            train_dataset=dataset_tokenized,
            max_seq_length=512, # 최대 시퀀스 길이
            args=self.train_args,
            dataset_text_field="text",
            data_collator=self.collate_fn
        )

        logging.info('[INFO] Trainer: Training Start')
        self.train(self.model, self.trainer)
        logging.info('[INFO] Trainer: Done Training')

        return self.save_model_path

    def load_model_n_tokenizer(self, base_model_name):
        model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            quantization_config=self.nf4_config,
            device_map="auto"
        )

        tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)

        return model, tokenizer

    def generate_prompt(self, data_point):
        prompt_template = """
        아래는 전화 통화 내용을 기반으로 한 지시사항입니다. 이에 대한 적절한 응답을 작성해주세요.

        ### 지시사항 (통화 내용):
        {instruction}

        ### 응답:
        """

        instruction = data_point["instruction"]
        label = data_point["output"]

        res = prompt_template.format(instruction=instruction)

        if label: res = f"{res}{label}<|im_end|>" # eos_token을 마지막에 추가

        data_point['text'] = res

        return data_point
    
    def tokenize_function(self, examples):
        outputs = self.tokenizer(examples["text"], truncation=True, max_length=512)
        return outputs
    
    def collate_fn(self, examples):
        examples_batch = self.tokenizer.pad(examples, padding='longest', return_tensors='pt')
        examples_batch['labels'] = examples_batch['input_ids'] # 모델 학습 평가를 위한 loss 계산을 위해 입력 토큰을 레이블로 사용
        return examples_batch
    
    def train_n_save(self, model, trainer):
        model.config.use_cache = False
        trainer.train()

        trainer.model.save_pretrained(self.save_model_path)
