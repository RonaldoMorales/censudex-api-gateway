from fastapi import Header, HTTPException
from app.services import auth_service

async def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Formato de token invalido")
    
    token = authorization.split(" ")[1]
    
    try:
        user_data = await auth_service.validate_token(token)
        return user_data
    except HTTPException as e:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")