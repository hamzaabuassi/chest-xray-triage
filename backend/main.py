from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routes import auth_routes
from database import engine, Base
from routes import scan_routes

# ---- Create DB tables on startup (if they don't exist) ----
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chest X-Ray Triage API",
    description="Explainable AI pneumonia detection with Grad-CAM triage tiers",
    version="1.0.0"
)

# ---- CORS: allow React frontend to call this API ----
# Update allow_origins with your actual frontend URL once deployed
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server default
        "https://chest-xray-triage-1.onrender.com",   # fallback if you use CRA-style port
        # "https://your-frontend-domain.vercel.app",  # add once deployed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Serve uploaded/generated images (original + Grad-CAM) statically ----
os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/gradcam", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ---- Routers ----
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(scan_routes.router, prefix="/scans", tags=["Scans"])


@app.get("/")
def root():
    return {"status": "ok", "message": "Chest X-Ray Triage API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)