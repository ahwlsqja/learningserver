# Execute
```
uvicorn app.main:app --reload
```

## Installation
```
pip install fastapi
pip install "uvicorn[standard]"
pip install aiohttp
pip install python-dotenv
```

## docker build
```
docker buildx build --platform linux/amd64 -t trainserver .
docker tag trainserver phoonil/trainserver:latest
docker push phoonil/trainserver:latest
```

## GPU 최소사양
- 8 bit 양자화 기준: 16GB

## Project Architecture
##### 개발언어
- Python

##### 개발 툴
- VS Code

##### 프레임워크
- Fastapi

##### API
- 사용자 맞춤형 모델 QLoRa 어댑터 생성을 위한 증강된 사용자 input 데이터를 불러오기 위한 AWS S3 사용
- QLoRa 어댑터 학습을 위한 trl SFTTrainer 사용
- 학습 완료된 모델 업로드를 위한 AWS S3 사용

##### 라이브러리
- fastapi
- aiohttp
- torch
- transformers
- peft
- pandas
- trl
- huggingface datasets

##### 형상관리 도구
- Git