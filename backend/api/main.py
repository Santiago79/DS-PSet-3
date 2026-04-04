from fastapi import FastAPI
from infrastructure import models
from infrastructure.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpsCenter API")

@app.get("/")
def read_root():
    return {"message": "API de OpsCenter funcionando correctamente"}