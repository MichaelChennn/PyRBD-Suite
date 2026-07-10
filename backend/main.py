from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import topologies, analysis

app = FastAPI(
    title="PyRBD-Suite API",
    description="Backend API for Reliability Block Diagram Analysis",
    version="1.0.0"
)

# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(topologies.router, prefix="/api/topologies", tags=["Topologies"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
