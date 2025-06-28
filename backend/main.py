from fastapi import FastAPI, status
from routers.document import router as document
from routers.label import router as label


<<<<<<< HEAD
app = FastAPI(title="Authorization NAUFFAR | PIPSA", )
app.include_router(router)
=======
app = FastAPI(title="Authorization NAUFFAR | PIPSA *** TEST ***", )
app.include_router(document)
app.include_router(label)
>>>>>>> developer


@app.get('/', status_code=status.HTTP_200_OK, tags=['Home'])
async def index():
    return {
        "Message": "Welcome to authorization NAUFFAR | PIPSA"
    }