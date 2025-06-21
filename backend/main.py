from fastapi import FastAPI, status
from routers.document import router


app = FastAPI(title="Authorization NAUFFAR | PIPSA *** TEST ***", )
app.include_router(router)


@app.get('/', status_code=status.HTTP_200_OK, tags=['Home'])
async def index():
    return {
        "Message": "Welcome to authorization NAUFFAR | PIPSA *** TEST ***"
    }