from fastapi import FastAPI
from app import models, database
from app.routes import router

app = FastAPI()

# Include the routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
