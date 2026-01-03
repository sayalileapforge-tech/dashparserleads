"""FastAPI application initialization and configuration."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import leads, process, sync, events
# Import models to register them with SQLAlchemy Base
from app.models.lead import Lead

# Initialize FastAPI app (don't try to create tables yet)
app = FastAPI(
    title="Insurance Leads API",
    description="Lead management system for Meta Lead Ads integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(leads.router)
app.include_router(process.router)
app.include_router(sync.router)
app.include_router(events.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
    }


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "message": "Insurance Leads API",
        "docs": "/docs",
        "health": "/health",
    }


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup."""
    from app.core.database import Base, engine
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created/verified successfully")
    except Exception as e:
        print(f"⚠ Warning during table creation: {e}")
        print("Tables may already exist or database might be offline. Proceeding anyway...")
    # Don't raise exception - let the app continue to run


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    pass
