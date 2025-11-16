import grpc
from app.grpc import orders_pb2, orders_pb2_grpc
import os

class OrdersGrpcClient:
    def __init__(self):
        host = os.getenv('ORDERS_GRPC_HOST', 'localhost')
        port = os.getenv('ORDERS_GRPC_PORT', '50052')
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = orders_pb2_grpc.OrderServiceStub(self.channel)
    
    def create_order(self, data):
        request = orders_pb2_grpc.CreateOrdersRequest(**data)
        return self.stub.CreateOrder(request)
    
    def get_all_orders(self, filters=None):
        if filters is None:
            filters = {}
        request = orders_pb2_grpc.GetAllOrdersRequest(**filters)
        return self.stub.GetAllOrders(request)
    
    def get_order_by_id(self, order_id):
        request = orders_pb2_grpc.GetOrderByIdRequest(id=order_id)
        return self.stub.GetOrderById(request)
    
    def update_order_status(self, order_id, data):
        request = orders_pb2_grpc.UpdateOrderStatusRequest(id=order_id, **data)
        return self.stub.UpdateOrderStatus(request)
    
    def delete_order(self, order_id):
        request = orders_pb2_grpc.DeleteOrderRequest(id=order_id)
        return self.stub.DeleteOrder(request)
    
    def close(self):
        self.channel.close()