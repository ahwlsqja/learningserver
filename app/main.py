import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.router import router

# from .service.data import 

app = FastAPI(
    title='Voip ML Server API',
    summary='API Endpoints for ML Calls',
    openapi_tags=[
        router.metadata,
    ],
    docs_url='/',
)

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router.router)
