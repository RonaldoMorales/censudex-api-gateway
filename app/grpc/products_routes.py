from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from app.grpc.products_grpc_client import ProductsGrpcClient
from app.middleware.auth_middleware import verify_token
import grpc

router = APIRouter(prefix="/api/products", tags=["products"])

# ===== MODELOS PYDANTIC =====

class CreateProductRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Nombre del producto")
    category: str = Field(..., description="Categoría del producto")
    price: float = Field(..., gt=0, description="Precio del producto")
    imageUrl: str = Field(default="", description="URL de la imagen")

class UpdateProductRequest(BaseModel):
    name: str = Field(..., min_length=1)
    category: str
    price: float = Field(..., gt=0)
    imageUrl: str = Field(default="")

# ===== ENDPOINTS =====

@router.get("/")
async def get_all_products():
    """
    Obtener todos los productos
    No requiere autenticación
    """
    grpc_client = ProductsGrpcClient()
    try:
        response = grpc_client.get_all_products()
        
        # Convertir productos de protobuf a dict
        products = [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "price": p.price,
                "imageUrl": p.imageUrl,
                "imagePublicId": p.imagePublicId,
                "isActive": p.isActive,
                "dateCreated": p.dateCreated
            }
            for p in response.products
        ]
        
        return {
            "success": response.success,
            "message": response.message,
            "count": response.count,
            "products": products
        }
    
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error gRPC: {e.details()}"
        )
    finally:
        grpc_client.close()


@router.get("/{product_id}")
async def get_product_by_id(product_id: str):
    """
    Obtener un producto por ID
    No requiere autenticación
    """
    grpc_client = ProductsGrpcClient()
    try:
        response = grpc_client.get_product_by_id(product_id)
        
        if not response.success:
            raise HTTPException(status_code=404, detail=response.message)
        
        product = {
            "id": response.product.id,
            "name": response.product.name,
            "category": response.product.category,
            "price": response.product.price,
            "imageUrl": response.product.imageUrl,
            "imagePublicId": response.product.imagePublicId,
            "isActive": response.product.isActive,
            "dateCreated": response.product.dateCreated
        }
        
        return {
            "success": response.success,
            "message": response.message,
            "product": product
        }
    
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error gRPC: {e.details()}"
        )
    finally:
        grpc_client.close()


@router.post("/")
async def create_product(
    product_data: CreateProductRequest,
    user_data: dict = Depends(verify_token)
):
    """
    Crear un nuevo producto
    Requiere autenticación (token)
    """
    grpc_client = ProductsGrpcClient()
    try:
        response = grpc_client.create_product(product_data.dict())
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        
        product = {
            "id": response.product.id,
            "name": response.product.name,
            "category": response.product.category,
            "price": response.product.price,
            "imageUrl": response.product.imageUrl,
            "imagePublicId": response.product.imagePublicId,
            "isActive": response.product.isActive,
            "dateCreated": response.product.dateCreated
        }
        
        return {
            "success": response.success,
            "message": response.message,
            "product": product
        }
    
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error gRPC: {e.details()}"
        )
    finally:
        grpc_client.close()


@router.put("/{product_id}")
async def update_product(
    product_id: str,
    product_data: UpdateProductRequest,
    user_data: dict = Depends(verify_token)
):
    """
    Actualizar un producto existente
    Requiere autenticación (token)
    """
    grpc_client = ProductsGrpcClient()
    try:
        response = grpc_client.update_product(product_id, product_data.dict())
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        
        product = {
            "id": response.product.id,
            "name": response.product.name,
            "category": response.product.category,
            "price": response.product.price,
            "imageUrl": response.product.imageUrl,
            "imagePublicId": response.product.imagePublicId,
            "isActive": response.product.isActive,
            "dateCreated": response.product.dateCreated
        }
        
        return {
            "success": response.success,
            "message": response.message,
            "product": product
        }
    
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error gRPC: {e.details()}"
        )
    finally:
        grpc_client.close()


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    user_data: dict = Depends(verify_token)
):
    """
    Eliminar un producto (soft delete)
    Requiere autenticación (token)
    """
    grpc_client = ProductsGrpcClient()
    try:
        response = grpc_client.delete_product(product_id)
        
        if not response.success:
            raise HTTPException(status_code=404, detail=response.message)
        
        return {
            "success": response.success,
            "message": response.message
        }
    
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error gRPC: {e.details()}"
        )
    finally:
        grpc_client.close()