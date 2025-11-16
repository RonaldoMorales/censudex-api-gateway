import grpc
from app.grpc import products_pb2, products_pb2_grpc
import os

class ProductsGrpcClient:
    def __init__(self):
        host = os.getenv('PRODUCTS_GRPC_HOST', 'localhost')
        port = os.getenv('PRODUCTS_GRPC_PORT', '50052')
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = products_pb2_grpc.ProductServiceStub(self.channel)
    
    def get_all_products(self):
        """Obtener todos los productos"""
        request = products_pb2.GetAllProductsRequest()
        return self.stub.GetAllProducts(request)
    
    def get_product_by_id(self, product_id):
        """Obtener un producto por ID"""
        request = products_pb2.GetProductByIdRequest(id=product_id)
        return self.stub.GetProductById(request)
    
    def create_product(self, data):
        """Crear un nuevo producto"""
        request = products_pb2.CreateProductRequest(
            name=data.get('name'),
            category=data.get('category'),
            price=data.get('price'),
            imageUrl=data.get('imageUrl', '')
        )
        return self.stub.CreateProduct(request)
    
    def update_product(self, product_id, data):
        """Actualizar un producto existente"""
        request = products_pb2.UpdateProductRequest(
            id=product_id,
            name=data.get('name'),
            category=data.get('category'),
            price=data.get('price'),
            imageUrl=data.get('imageUrl', '')
        )
        return self.stub.UpdateProduct(request)
    
    def delete_product(self, product_id):
        """Eliminar un producto (soft delete)"""
        request = products_pb2.DeleteProductRequest(id=product_id)
        return self.stub.DeleteProduct(request)
    
    def close(self):
        """Cerrar la conexión"""
        self.channel.close()