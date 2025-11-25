from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import nft, marketplace, auction, database, ipfs, user, email
from .services.indexer_service import indexer_service
import asyncio

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for NFT Marketplace with blockchain integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.on_event("startup")
async def startup_event():
    """Start the blockchain indexer in the background"""
    asyncio.create_task(indexer_service.sync_events())

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(nft.router, prefix=settings.API_V1_PREFIX)
app.include_router(marketplace.router, prefix=settings.API_V1_PREFIX)
app.include_router(auction.router, prefix=settings.API_V1_PREFIX)
app.include_router(database.router, prefix=settings.API_V1_PREFIX)
app.include_router(ipfs.router, prefix=settings.API_V1_PREFIX)
app.include_router(user.router, prefix=settings.API_V1_PREFIX)
app.include_router(email.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "NFT Marketplace API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
