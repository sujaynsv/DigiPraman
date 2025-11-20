from fastapi import FastAPI
from app.routers import health

app = FastAPI(title="Loan Utilization Tracker Backend")

# Include routes
app.include_router(health.router, prefix="/health", tags=["Health"])
