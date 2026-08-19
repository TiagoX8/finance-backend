from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.transactions import router as transactions_router
from app.routes.categories import router as categories_router
from app.routes.auth import router as auth_router

app = FastAPI(title="Finance SaaS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(categories_router)


@app.get("/")
def root():
    return {"message": "Finance SaaS API running"}