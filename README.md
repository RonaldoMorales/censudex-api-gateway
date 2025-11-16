# Censudex API Gateway

API Gateway para el sistema de microservicios Censudex. Actúa como punto de entrada único para todos los servicios, manejando autenticación, enrutamiento y traducción de protocolos HTTP a gRPC.

## Arquitectura

Este proyecto implementa el patrón **API Gateway** utilizando FastAPI (Python). Recibe peticiones HTTP de clientes externos y las traduce a llamadas gRPC hacia los microservicios internos.

### Patrón de Diseño

- **API Gateway Pattern**: Punto de entrada único que centraliza el acceso a los microservicios
- **Adapter Pattern**: Traduce peticiones HTTP a gRPC
- **Middleware Pattern**: Validación de tokens JWT para autenticación

### Comunicación

- **HTTP** para comunicación con Auth Service
- **gRPC** para comunicación con Clients, Products y Orders Services

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/RonaldoMorales/censudex-api-gateway.git
cd censudex-api-gateway
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Windows PowerShell:**
```bash
.\venv\Scripts\Activate
```

**Windows CMD:**
```bash
venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
PORT=3000
AUTH_SERVICE_URL=http://localhost:3002/api/auth
CLIENTS_SERVICE_URL=http://localhost:3001/api/clients
CLIENTS_GRPC_HOST=localhost
CLIENTS_GRPC_PORT=50051
PRODUCTS_GRPC_HOST=localhost
PRODUCTS_GRPC_PORT=50052
ORDERS_GRPC_HOST=localhost
ORDERS_GRPC_PORT=50053
NODE_ENV=development
```

## Ejecución

### Modo desarrollo (1 instancia)

```bash
python run.py
```

El servidor estará disponible en `http://localhost:3000`

### Modo producción (múltiples instancias para balanceo)

**Instancia 1 (puerto 3000):**
```bash
python run.py
```

**Instancia 2 (puerto 3100):**
```bash
python run.py .env.instance2
```

**Instancia 3 (puerto 3200):**
```bash
python run.py .env.instance3
```

## Endpoints Disponibles

### Autenticación

- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/validate-token` - Validar token JWT
- `POST /api/auth/logout` - Cerrar sesión

### Clientes

- `POST /api/clients` - Crear cliente (público)
- `GET /api/clients` - Obtener todos los clientes (requiere token)
- `GET /api/clients/{id}` - Obtener cliente por ID (requiere token)
- `PATCH /api/clients/{id}` - Actualizar cliente (requiere token)
- `PATCH /api/clients/{id}/password` - Actualizar contraseña (requiere token)
- `DELETE /api/clients/{id}` - Eliminar cliente (requiere token)

### Productos

- `GET /api/products` - Obtener todos los productos 
- `GET /api/products/{id}` - Obtener producto por ID 
- `POST /api/products` - Crear producto 
- `PATCH /api/products/{id}` - Actualizar producto 
- `DELETE /api/products/{id}` - Eliminar producto 

### Pedidos

- `GET /api/orders` - Obtener todos los pedidos 
- `GET /api/orders/{id}` - Obtener pedido por ID 
- `POST /api/orders` - Crear pedido 
- `PATCH /api/orders/{id}` - Actualizar pedido 
- `DELETE /api/orders/{id}` - Eliminar pedido 

### Health Check

- `GET /health` - Verificar estado del servicio

## Estructura del Proyecto

```
censudex-api-gateway/
├── app/
│   ├── grpc/
│   │   ├── clients_pb2.py
│   │   ├── clients_pb2_grpc.py
│   │   ├── clients_grpc_client.py
│   │   ├── products_pb2.py
│   │   ├── products_pb2_grpc.py
│   │   ├── products_grpc_client.py
│   │   ├── orders_pb2.py
│   │   ├── orders_pb2_grpc.py
│   │   └── orders_grpc_client.py
│   ├── middleware/
│   │   └── auth_middleware.py
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── clients_routes.py
│   │   ├── products_routes.py
│   │   └── orders_routes.py
│   ├── services/
│   │   └── auth_service.py
│   └── main.py
├── proto/
│   ├── clients.proto
│   ├── products.proto
│   └── orders.proto
├── .env
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## Autenticación

La API Gateway utiliza JWT (JSON Web Tokens) para autenticación.

### Obtener un token

```bash
POST http://localhost:3000/api/auth/login
Content-Type: application/json

{
  "identifier": "admin@censudex.cl",
  "password": "Admin123!"
}
```

### Usar el token

```bash
GET http://localhost:3000/api/clients
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Integración con NGINX

Para balanceo de carga, NGINX distribuye las peticiones entre las 3 instancias de la API Gateway.

### Configuración NGINX

```nginx
upstream api_gateway_cluster {
    server localhost:3000;
    server localhost:3100;
    server localhost:3200;
}

server {
    listen 80;
    location / {
        proxy_pass http://api_gateway_cluster;
    }
}
```

Acceso a través de NGINX: `http://localhost:80/api/...`

## Desarrollo

### Regenerar archivos gRPC

Si modificas los archivos .proto, regenera los archivos Python:

```bash
python -m grpc_tools.protoc -I./proto --python_out=./app/grpc --grpc_python_out=./app/grpc ./proto/clients.proto
python -m grpc_tools.protoc -I./proto --python_out=./app/grpc --grpc_python_out=./app/grpc ./proto/products.proto
python -m grpc_tools.protoc -I./proto --python_out=./app/grpc --grpc_python_out=./app/grpc ./proto/orders.proto
```

Luego arregla los imports en los archivos `*_pb2_grpc.py`:

Cambia:
```python
import clients_pb2 as clients__pb2
```

Por:
```python
from . import clients_pb2 as clients__pb2
```

## Troubleshooting

### Error: Module not found

Asegúrate de haber activado el entorno virtual:
```bash
.\venv\Scripts\Activate
pip install -r requirements.txt
```

### Error: Connection refused

Verifica que los servicios backend estén corriendo:
- Clients Service en puerto 3001 (HTTP) y 50051 (gRPC)
- Auth Service en puerto 3002
- Products Service en puerto 3003 (HTTP) y 50052 (gRPC)
- Orders Service en puerto 3004 (HTTP) y 50053 (gRPC)

### Error: Token inválido

El token debe ir en el header `Authorization` con el formato:
```
Authorization: Bearer TU_TOKEN_AQUI
```

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **gRPC**: Comunicación eficiente con microservicios
- **Protocol Buffers**: Serialización de datos
- **httpx**: Cliente HTTP asíncrono
- **pydantic**: Validación de datos

## Autores

- Ronaldo Morales
- Dantte Marquez
- German Morales

## Licencia

Este proyecto es parte del curso de Arquitectura de Sistemas - Universidad Católica del Norte
