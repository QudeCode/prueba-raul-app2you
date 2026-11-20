from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import entidades  # noqa: F401  registra todas las entidades antes de la primera consulta
from app.recursos import controller as recursos_controller
from app.usuarios import controller as usuarios_controller

app = FastAPI()

# El frontend de desarrollo (ng serve) llama a la API desde otro origen
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:4200"])

app.include_router(usuarios_controller.router)
app.include_router(recursos_controller.router)
