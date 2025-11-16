from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Importa las rutas de cada microservicio expuestas por el gateway
from app.routes import auth_routes, clients_routes, products_routes, orders_routes

# Carga variables de entorno desde .env
load_dotenv()

# Inicializa la aplicación FastAPI con metadatos
app = FastAPI(
    title="Censudex API Gateway",
    description="API Gateway para microservicios de Censudex",
    version="1.0.0"
)

# Configuración de CORS para permitir llamadas desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Acepta peticiones de cualquier dominio
    allow_credentials=True,
    allow_methods=["*"],           # Permite todos los métodos HTTP
    allow_headers=["*"],           # Permite todos los headers
)

# Registrar routers que redirigen solicitudes a los microservicios
app.include_router(auth_routes.router)
app.include_router(clients_routes.router)
app.include_router(products_routes.router)
app.include_router(orders_routes.router)

# Endpoint de salud para verificar que el API Gateway está activo
@app.get("/health")
async def health_check():
    return {"status": "OK", "service": "API Gateway"}

# Ruta raíz de presentación
@app.get("/")
async def root():
    return {"message": "Censudex API Gateway", "version": "1.0.0"}

# Arranque del servidor cuando se ejecuta directamente este archivo
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))    # Puerto definido en .env o 3000 por defecto
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
