from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.routes import auth_routes, clients_routes, products_routes

load_dotenv()

app = FastAPI(
    title="Censudex API Gateway",
    description="API Gateway para microservicios de Censudex",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(clients_routes.router)
app.include_router(products_routes.router)

@app.get("/health")
async def health_check():
    return {"status": "OK", "service": "API Gateway"}

@app.get("/")
async def root():
    return {"message": "Censudex API Gateway", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)