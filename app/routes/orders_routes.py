from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Asume que este módulo existe y contiene el OrdersGrpcClient
from app.grpc.orders_grpc_client import OrdersGrpcClient
from app.middleware.auth_middleware import verify_token
import grpc

# Inicializa el router para las rutas de pedidos
router = APIRouter(prefix="/api/orders", tags=["orders"])

# --- Modelos Pydantic para la entrada HTTP (REQUESTS) ---

# Modelo para un item al crear un pedido
class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int

# Modelo para crear un pedido completo
class CreateOrderRequest(BaseModel):
    user_id: int
    delivery_address: str
    items_to_create: List[OrderItemRequest]

# Modelo para actualizar el estado de un pedido
class UpdateStatusRequest(BaseModel):
    new_status: str
    tracking_number: Optional[str] = None

# Modelo para cancelar/eliminar un pedido
class DeleteOrderRequest(BaseModel):
    cancellation_reason: Optional[str] = None


# --- Rutas HTTP (API REST) ---

@router.post("/")
async def create_order(order_data: CreateOrderRequest, user_data: dict = Depends(verify_token)):
    """
    Crea un nuevo pedido utilizando la llamada gRPC al OrderManager.
    """
    grpc_client = OrdersGrpcClient()
    try:
        # 1. Preparar la estructura de datos para gRPC
        items_grpc = [
            grpc_client.orders_pb2.OrderItemRequest(
                product_id=item.product_id,
                quantity=item.quantity
            )
            for item in order_data.items_to_create
        ]

        # 2. Construir el request gRPC
        grpc_request = grpc_client.orders_pb2.CreateOrderRequest(
            user_id=order_data.user_id,
            delivery_address=order_data.delivery_address,
            items_to_create=items_grpc
        )

        # 3. Llamar al servicio gRPC
        response = grpc_client.create_order(grpc_request)
        
        # 4. Devolver la respuesta formateada
        return {
            "message": response.message,
            "order": {
                "id": response.id,
                "user_id": response.user_id,
                "total_amount": response.total_amount,
                "current_status": response.current_status,
                "delivery_address": response.delivery_address,
                "order_date": response.order_date.ToDatetime().isoformat() if response.order_date else None,
                "items_count": len(response.items)
            }
        }
    except grpc.RpcError as e:
        # Manejo de errores gRPC (ej: validación, falta de stock)
        raise HTTPException(status_code=400, detail=str(e.details()))
    finally:
        grpc_client.close()


@router.get("/")
async def get_all_orders(
    user_data: dict = Depends(verify_token),
    order_id: Optional[int] = Query(None, description="ID del pedido"),
    user_id: Optional[int] = Query(None, description="ID del cliente"),
    status: Optional[str] = Query(None, description="Estado actual del pedido (PENDIENTE, ENVIADO, etc.)"),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (ISO 8601)")
):
    """
    Consulta todos los pedidos aplicando filtros opcionales.
    """
    grpc_client = OrdersGrpcClient()
    try:
        # 1. Convertir filtros de Python a Timestamp de gRPC si existen
        from google.protobuf.timestamp_pb2 import Timestamp
        
        start_ts, end_ts = None, None
        if start_date:
            start_ts = Timestamp()
            start_ts.FromDatetime(start_date)
        if end_date:
            end_ts = Timestamp()
            end_ts.FromDatetime(end_date)
            
        # 2. Construir el request gRPC
        grpc_request = grpc_client.orders_pb2.GetOrdersRequest(
            order_id=order_id if order_id is not None else 0,
            user_id=user_id if user_id is not None else 0,
            current_status=status if status is not None else "",
            start_date=start_ts,
            end_date=end_ts
        )

        # 3. Llamar al servicio gRPC
        response = grpc_client.get_orders(grpc_request)
        
        # 4. Devolver la respuesta formateada
        orders_list = []
        for order in response.orders:
            orders_list.append({
                "id": order.id,
                "user_id": order.user_id,
                "total_amount": order.total_amount,
                "current_status": order.current_status,
                "order_date": order.order_date.ToDatetime().isoformat() if order.order_date else None,
                "tracking_number": order.tracking_number
                # NOTA: Opcionalmente, aquí puedes incluir los ítems si es necesario
            })
            
        return {"count": response.count, "orders": orders_list}
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=str(e.details()))
    finally:
        grpc_client.close()


@router.get("/{order_id}")
async def get_order_by_id(order_id: int, user_data: dict = Depends(verify_token)):
    """
    Obtiene los detalles completos de un pedido por su ID.
    """
    grpc_client = OrdersGrpcClient()
    try:
        # 1. Construir el request gRPC
        grpc_request = grpc_client.orders_pb2.GetOrderByIdRequest(id=order_id)

        # 2. Llamar al servicio gRPC
        response = grpc_client.get_order_by_id(grpc_request)
        
        # 3. Formatear la respuesta (incluyendo ítems)
        items_list = [{
            "item_id": item.item_id, 
            "product_id": item.product_id, 
            "quantity": item.quantity, 
            "price_at_purchase": item.price_at_purchase
        } for item in response.items]
        
        return {
            "order": {
                "id": response.id,
                "user_id": response.user_id,
                "total_amount": response.total_amount,
                "current_status": response.current_status,
                "order_date": response.order_date.ToDatetime().isoformat() if response.order_date else None,
                "delivery_address": response.delivery_address,
                "tracking_number": response.tracking_number,
                "items": items_list
            }
        }
    except grpc.RpcError as e:
        # gRPC lanza un error 404 para "No encontrado"
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    finally:
        grpc_client.close()


@router.patch("/{order_id}/status")
async def update_order_status(order_id: int, status_data: UpdateStatusRequest, user_data: dict = Depends(verify_token)):
    """
    Actualiza el estado de un pedido (ej: de PENDIENTE a ENVIADO).
    """
    grpc_client = OrdersGrpcClient()
    try:
        # 1. Construir el request gRPC
        grpc_request = grpc_client.orders_pb2.UpdateStatusRequest(
            id=order_id,
            new_status=status_data.new_status,
            tracking_number=status_data.tracking_number if status_data.tracking_number else ""
        )

        # 2. Llamar al servicio gRPC
        response = grpc_client.update_order_status(grpc_request)
        
        # 3. Devolver la respuesta formateada
        return {
            "message": response.message,
            "order": {
                "id": response.id,
                "current_status": response.current_status,
                "updated_at": response.updated_at
            }
        }
    except grpc.RpcError as e:
        raise HTTPException(status_code=400, detail=str(e.details()))
    finally:
        grpc_client.close()


@router.delete("/{order_id}")
async def delete_order(order_id: int, delete_data: DeleteOrderRequest, user_data: dict = Depends(verify_token)):
    """
    Cancela/elimina un pedido.
    """
    grpc_client = OrdersGrpcClient()
    try:
        # 1. Construir el request gRPC
        grpc_request = grpc_client.orders_pb2.DeleteOrderRequest(
            id=order_id,
            cancellation_reason=delete_data.cancellation_reason if delete_data.cancellation_reason else ""
        )

        # 2. Llamar al servicio gRPC
        response = grpc_client.delete_order(grpc_request)
        
        # 3. Devolver la respuesta simple
        return {"message": response.message}
    except grpc.RpcError as e:
        raise HTTPException(status_code=404, detail="Pedido no encontrado o no puede ser cancelado")
    finally:
        grpc_client.close()