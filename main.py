from fastapi import FastAPI
from fastapi.responses import Response


app = FastAPI()


@app.get('/')
def index():
    return Response('Hello world')