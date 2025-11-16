from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.grpc.products_grpc_client import ProductsGrpcClient
from app.middleware.auth_middleware import verify_token
import grpc

# Router para manejar todas las rutas relacionadas con productos
router = APIRouter(prefix="/api/products", tags=["products"])

# Modelo para crear un producto (datos obligatorios)
class CreateProductRequest(BaseModel):
    name: str
    category: str
    price: float
    imageUrl: str

# Modelo para actualizar un producto (todos opcionales)
class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    imageUrl: Optional[str] = None

# Obtener todos los productos
@router.get("/")
async def get_all_products(user_data: dict = Depends(verify_token)):
    grpc_client = ProductsGrpcClient()
    try:
        response = grpc_client.get_all_products()

        # Si gRPC indica que falló, se retorna error HTTP
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        
        # Formatear productos para la API Gateway
        products = []
        for product in response.products:
            products.append({
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "imageUrl": product.imageUrl,
                "imagePublicId": product.imagePublicId,
                "isActive": product.isActive,
                "dateCreated": product.dateCreated
            })

        return {"success": True, "count": response.count, "products": products}
    except grpc.RpcError as e:
        # Error al comunicarse mediante gRPC
        raise HTTPException(status_code=500, detail=str(e.details()))
    finally:
        grpc_client.close()

# Obtener un producto por ID
@router.get("/{product_id}")
async def get_product_by_id(product_id: str, user_data: dict = Depends(verify_token)):
    grpc_client = ProductsGrpcClient()
    try:
        response = grpc_client.get_product_by_id(product_id)

        if not response.success:
            raise HTTPException(status_code=404, detail=response.message)
        
        product = response.product

        return {
            "success": True,
            "product": {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "imageUrl": product.imageUrl,
                "imagePublicId": product.imagePublicId,
                "isActive": product.isActive,
                "dateCreated": product.dateCreated
            }
        }
    except grpc.RpcError:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    finally:
        grpc_client.close()

# Crear un nuevo producto
@router.post("/")
async def create_product(product_data: CreateProductRequest, user_data: dict = Depends(verify_token)):
    grpc_client = ProductsGrpcClient()
    try:
        response = grpc_client.create_product(product_data.dict())

        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)

        product = response.product

        return {
            "success": True,
            "message": response.message,
            "product": {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "imageUrl": product.imageUrl,
                "imagePublicId": product.imagePublicId,
                "isActive": product.isActive,
                "dateCreated": product.dateCreated
            }
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=400, detail=str(e.details()))
    finally:
        grpc_client.close()

# Actualizar parcialmente un producto
@router.patch("/{product_id}")
async def update_product(product_id: str, product_data: UpdateProductRequest, user_data: dict = Depends(verify_token)):
    grpc_client = ProductsGrpcClient()
    try:
        # Eliminamos campos None para no enviar datos no modificados
        data = {k: v for k, v in product_data.dict().items() if v is not None}

        response = grpc_client.update_product(product_id, data)

        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)

        product = response.product

        return {
            "success": True,
            "message": response.message,
            "product": {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "imageUrl": product.imageUrl,
                "imagePublicId": product.imagePublicId,
                "isActive": product.isActive,
                "dateCreated": product.dateCreated
            }
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=400, detail=str(e.details()))
    finally:
        grpc_client.close()

# Eliminar un producto (lógica soft delete en el microservicio)
@router.delete("/{product_id}")
async def delete_product(product_id: str, user_data: dict = Depends(verify_token)):
    grpc_client = ProductsGrpcClient()
    try:
        response = grpc_client.delete_product(product_id)

        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        
        return {"success": True, "message": response.message}
    except grpc.RpcError:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    finally:
        grpc_client.close()
