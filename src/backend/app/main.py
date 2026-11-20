from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import entidades  # noqa: F401  registra todas las entidades antes de la primera consulta
from app.common.errores import (
    Conflicto,
    ErrorDominio,
    NoAutenticado,
    NoEncontrado,
    NoPermitido,
    ReglaIncumplida,
)
from app.recursos import controller as recursos_controller
from app.usuarios import controller as usuarios_controller

app = FastAPI()

# El frontend de desarrollo (ng serve) llama a la API desde otro origen; los POST y la
# cabecera X-Usuario-Id necesitan pasar el preflight
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Usuario-Id"],
)

# Traducción única de los errores del dominio a HTTP (decisión 0012)
ESTADO_HTTP: dict[type[ErrorDominio], int] = {
    NoEncontrado: 404,
    NoAutenticado: 401,
    NoPermitido: 403,
    ReglaIncumplida: 400,
    Conflicto: 409,
}


@app.exception_handler(ErrorDominio)
def manejar_error_dominio(_: Request, error: ErrorDominio) -> JSONResponse:
    return JSONResponse(status_code=ESTADO_HTTP[type(error)], content={"detail": str(error)})


app.include_router(usuarios_controller.router)
app.include_router(recursos_controller.router)
