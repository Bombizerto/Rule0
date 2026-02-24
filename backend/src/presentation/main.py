from fastapi import FastAPI

# Inicializamos la instacia de nuestra aplicación
app = FastAPI(
    title="Rule Zero API",
    description="Backend para App Commander MTG",
    version="1.0.0"
)

# Endpoint básico de estado (Health Check)
@app.get("/")
def health_check():
    """Ruta para verificar que el servidor está funcionando."""
    return {"status": "ok", "message": "Rule Zero API is running"}
