from fastapi import Header, HTTPException
from app.services import auth_service

# Middleware encargado de validar el token enviado en las rutas protegidas
async def verify_token(authorization: str = Header(None)):
    # Si no viene encabezado Authorization → no se envió token
    if not authorization:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    # Validar que el formato sea "Bearer <token>"
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Formato de token invalido")
    
    # Extraer el token quitando "Bearer "
    token = authorization.split(" ")[1]
    
    try:
        # Llamar al servicio que valida el token contra el microservicio de autenticación
        user_data = await auth_service.validate_token(token)

        # Si es válido, se devuelve la información del usuario
        return user_data

    except HTTPException:
        # Cualquier error del microservicio → token inválido o expirado
        raise HTTPException(status_code=401, detail="Token invalido o expirado")
