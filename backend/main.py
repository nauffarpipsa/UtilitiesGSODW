from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from routers.document import router as document
from routers.label import router as label


app = FastAPI(title="Utilities GSO Nauffar", )

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes (puedes restringir a dominios específicos)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

app.include_router(document)
app.include_router(label)

# endpoint main
@app.get('/', status_code=status.HTTP_200_OK, tags=['Home'])
async def index():
    return {
        "Message": "Welcome to GSO utilities Nauffar"
    }