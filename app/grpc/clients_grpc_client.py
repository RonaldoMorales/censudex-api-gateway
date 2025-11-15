import grpc
from app.grpc import clients_pb2, clients_pb2_grpc
import os

class ClientsGrpcClient:
    def __init__(self):
        host = os.getenv('CLIENTS_GRPC_HOST', 'localhost')
        port = os.getenv('CLIENTS_GRPC_PORT', '50051')
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = clients_pb2_grpc.ClientServiceStub(self.channel)
    
    def create_client(self, data):
        request = clients_pb2.CreateClientRequest(**data)
        return self.stub.CreateClient(request)
    
    def get_all_clients(self, filters=None):
        if filters is None:
            filters = {}
        request = clients_pb2.GetAllClientsRequest(**filters)
        return self.stub.GetAllClients(request)
    
    def get_client_by_id(self, client_id, include_password=False):
        request = clients_pb2.GetClientByIdRequest(
            id=client_id,
            includePassword=include_password
        )
        return self.stub.GetClientById(request)
    
    def update_client(self, client_id, data):
        request = clients_pb2.UpdateClientRequest(id=client_id, **data)
        return self.stub.UpdateClient(request)
    
    def update_password(self, client_id, password):
        request = clients_pb2.UpdatePasswordRequest(id=client_id, password=password)
        return self.stub.UpdatePassword(request)
    
    def delete_client(self, client_id):
        request = clients_pb2.DeleteClientRequest(id=client_id)
        return self.stub.DeleteClient(request)
    
    def close(self):
        self.channel.close()