from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv
from routes import images, central_api

load_dotenv()

app = FastAPI(
    title=os.environ.get("API_TITLE"),
    description=os.environ.get("DESCRIPTION"),
    version=os.environ.get("VERSION")
)

app.include_router(images.router, prefix="/images")
app.include_router(central_api.router, prefix="/capi")

if __name__ == '__main__':
    uvicorn.run(app, host=os.environ.get('API_HOST'), port=int(os.environ.get("API_PORT")), debug=True)
