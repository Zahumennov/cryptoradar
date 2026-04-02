from fastapi import FastAPI
from contextlib import asynccontextmanager

from shared.database import engine, Base
from api.routes import auth, prices, alerts


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    print("Database tables created")
    yield
    # Shutdown
    print("App shutting down")


app = FastAPI(
    title="CryptoRadar",
    description="Crypto price tracking and alert system",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(prices.router, prefix="/prices", tags=["prices"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])


@app.get("/")
async def root():
    return {"message": "CryptoRadar API is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}