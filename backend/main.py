from fastapi import FastAPI, status
from routers.document import router as document
from routers.label import router as label


app = FastAPI(title="Utilities GSO NAUFFAR | PIPSA *** TEST ***", )

# add router's
app.include_router(document)
app.include_router(label)

# endpoint main
@app.get('/', status_code=status.HTTP_200_OK, tags=['Home'])
async def index():
    return {
        "Message": "Welcome to GSO utilities NAUFFAR | PIPSA *** TEST ***"
    }