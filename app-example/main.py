import os
from fastapi import FastAPI
from app_example.handlers.framework import router as framework_router

AUTH_SECRET = os.getenv("AUTH_SECRET")

app = FastAPI(title="Framework API", version="1.0.0")
app.include_router(framework_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
