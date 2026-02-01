from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, connections, query, settings
from app.core.config import settings as app_settings
from app.models.database import init_db

app = FastAPI(
    title="Universal RAG Platform",
    description="AI-powered database query system with RAG",
    version="1.0.0"
)

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(connections.router, prefix="/api/connections", tags=["connections"])
app.include_router(query.router, prefix="/api/query", tags=["query"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])

@app.get("/")
async def root():
    return {"message": "Universal RAG Platform API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
