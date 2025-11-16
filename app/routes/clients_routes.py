from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.grpc.clients_grpc_client import ClientsGrpcClient
from app.middleware.auth_middleware import verify_token
import grpc

# Router base para las rutas del microservicio de clientes
router = APIRouter(prefix="/api/clients", tags=["clients"])

# ----------- MODELOS DE REQUEST -----------

# Datos requeridos para crear un cliente nuevo
class CreateClientRequest(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    username: str
    password: str
    birthDate: str
    address: str
    phone: str

# Modelo para actualizar datos del cliente (campos opcionales)
class UpdateClientRequest(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    birthDate: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

# Modelo para actualizar únicamente la contraseña
class UpdatePasswordRequest(BaseModel):
    password: str

# ----------- ENDPOINTS -----------

# Crear un cliente (NO requiere autenticación)
@router.post("/")
async def create_client(client_data: CreateClientRequest):
    grpc_client = ClientsGrpcClient()
    try:
        # Llamada gRPC al microservicio de clientes
        response = grpc_client.create_client(client_data.dict())

        # Construcción de respuesta limpia hacia el cliente HTTP
        return {
            "message": response.message,
            "client": {
                "id": response.id,
                "firstName": response.firstName,
                "lastName": response.lastName,
                "email": response.email,
                "username": response.username,
                "role": response.role,
                "isActive": response.isActive,
                "birthDate": response.birthDate,
                "address": response.address,
                "phone": response.phone,
                "createdAt": response.createdAt
            }
        }
    except grpc.RpcError as e:
        # Captura errores gRPC y los traduce a HTTP
        raise HTTPException(status_code=400, detail=str(e.details()))
    finally:
        grpc_client.close()

# Obtener todos los clientes (requiere token válido)
@router.get("/")
async def get_all_clients(
    user_data: dict = Depends(verify_token),        # Validación JWT desde el middleware
    name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
    isActive: Optional[str] = Query(None)
):
    grpc_client = ClientsGrpcClient()
    try:
        # Construcción dinámica de filtros
        filters = {}
        if name: filters['name'] = name
        if email: filters['email'] = email
        if username: filters['username'] = username
        if isActive: filters['isActive'] = isActive
        
        # Petición al microservicio vía gRPC
        response = grpc_client.get_all_clients(filters)

        # Conversión de la lista de clientes gRPC → dict
        clients = []
        for client in response.clients:
            clients.append({
                "id": client.id,
                "firstName": client.firstName,
                "lastName": client.lastName,
                "email": client.email,
                "username": client.username,
                "role": client.role,
                "isActive": client.isActive,
                "birthDate": client.birthDate,
                "address": client.address,
                "phone": client.phone,
                "createdAt": client.createdAt
            })

        return {"count": response.count, "clients": clients}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=str(e.details()))
    finally:
        grpc_client.close()

# Obtener cliente por ID (requiere token)
@router.get("/{client_id}")
async def get_client_by_id(client_id: str, user_data: dict = Depends(verify_token)):
    grpc_client = ClientsGrpcClient()
    try:
        response = grpc_client.get_client_by_id(client_id)

        return {
            "client": {
                "id": response.id,
                "firstName": response.firstName,
                "lastName": response.lastName,
                "email": response.email,
                "username": response.username,
                "role": response.role,
                "isActive": response.isActive,
                "birthDate": response.birthDate,
                "address": response.address,
                "phone": response.phone,
                "createdAt": response.createdAt,
                "updatedAt": response.updatedAt
            }
        }
    except grpc.RpcError:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    finally:
        grpc_client.close()

# Actualizar cliente (requiere token)
@router.patch("/{client_id}")
async def update_client(client_id: str, client_data: UpdateClientRequest, user_data: dict = Depends(verify_token)):
    grpc_client = ClientsGrpcClient()
    try:
        # Remover campos None (solo actualizar lo enviado)
        data = {k: v for k, v in client_data.dict().items() if v is not None}

        response = grpc_client.update_client(client_id, data)

        return {
            "message": response.message,
            "client": {
                "id": response.id,
                "firstName": response.firstName,
                "lastName": response.lastName,
                "email": response.email,
                "username": response.username,
                "role": response.role,
                "isActive": response.isActive,
                "birthDate": response.birthDate,
                "address": response.address,
                "phone": response.phone,
                "updatedAt": response.updatedAt
            }
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=400, detail=str(e.details()))
    finally:
        grpc_client.close()

# Actualizar contraseña (requiere token)
@router.patch("/{client_id}/password")
async def update_password(client_id: str, password_data: UpdatePasswordRequest, user_data: dict = Depends(verify_token)):
    grpc_client = ClientsGrpcClient()
    try:
        response = grpc_client.update_password(client_id, password_data.password)
        return {"message": response.message}
    except grpc.RpcError as e:
        raise HTTPException(status_code=400, detail=str(e.details()))
    finally:
        grpc_client.close()

# Eliminar cliente (requiere token)
@router.delete("/{client_id}")
async def delete_client(client_id: str, user_data: dict = Depends(verify_token)):
    grpc_client = ClientsGrpcClient()
    try:
        response = grpc_client.delete_client(client_id)
        return {"message": response.message}
    except grpc.RpcError:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    finally:
        grpc_client.close()
