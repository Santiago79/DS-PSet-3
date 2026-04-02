from fastapi import FastAPI

app = FastAPI(title="OpsCenter API")

@app.get("/")
def read_root():
    return {"message": "API de OpsCenter funcionando correctamente"}