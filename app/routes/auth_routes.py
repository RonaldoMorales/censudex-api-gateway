from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    identifier: str
    password: str

@router.post("/login")
async def login(credentials: LoginRequest):
    return await auth_service.login(credentials.dict())

@router.get("/validate-token")
async def validate_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    token = authorization.split(" ")[1]
    return await auth_service.validate_token(token)

@router.post("/logout")
async def logout(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    token = authorization.split(" ")[1]
    return await auth_service.logout(token)