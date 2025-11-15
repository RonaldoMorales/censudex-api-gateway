import httpx
import os
from fastapi import HTTPException

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:3002/api/auth')

async def login(credentials):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{AUTH_SERVICE_URL}/login", json=credentials)
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail=response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Error conectando con Auth Service: {str(e)}")

async def validate_token(token):
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{AUTH_SERVICE_URL}/validate-token", headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail=response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Error conectando con Auth Service: {str(e)}")

async def logout(token):
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(f"{AUTH_SERVICE_URL}/logout", headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail=response.json())
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Error conectando con Auth Service: {str(e)}")