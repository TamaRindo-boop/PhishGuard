from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .evaluador_url import evaluar_url

app = FastAPI(title="API de Detección de Phishing")

# Esto permite que tu página web (frontend) se comunique con este backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definimos qué datos va a enviar el usuario (una URL)
class URLRequest(BaseModel):
    url: str

# Creamos la ruta para analizar la URL
@app.post("/api/analizar")
def analizar(request: URLRequest):
    try:
        resultado = evaluar_url(request.url)
        return {"success": True, "data": resultado}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Una ruta básica para comprobar que el servidor está vivo
@app.get("/")
def inicio():
    return {"mensaje": "Servidor backend funcionando correctamente"}