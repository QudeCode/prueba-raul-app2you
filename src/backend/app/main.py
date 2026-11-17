from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# El frontend de desarrollo (ng serve) llama a la API desde otro origen
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:4200"])


@app.get("/")
def hello() -> dict[str, str]:
    return {"message": "Hello world"}
