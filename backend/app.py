import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

from backend.database.db import init_db
from backend.services.scheduler_service import start_scheduler, stop_scheduler
from backend.routes.medication_routes import router as med_router
from backend.routes.interaction_routes import router as interact_router
from backend.routes.admin_routes import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    print("[INFO] MedMate Database initialized and scheduler started.")
    yield
    stop_scheduler()
    print("[INFO] MedMate Scheduler stopped.")

app = FastAPI(
    title="MedMate - AI Medication Companion",
    description="Zero-learning AI voice medication companion for senior citizens",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(med_router, prefix="/api")
app.include_router(interact_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "MedMate"}

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
os.makedirs(frontend_dir, exist_ok=True)

@app.get("/manifest.json")
def serve_manifest():
    return FileResponse(os.path.join(frontend_dir, 'manifest.json'), media_type='application/json')

@app.get("/sw.js")
def serve_sw():
    return FileResponse(os.path.join(frontend_dir, 'sw.js'), media_type='application/javascript')

@app.get("/calendar.html")
def serve_calendar():
    return FileResponse(os.path.join(frontend_dir, 'calendar.html'))

@app.get("/profile.html")
def serve_profile():
    return FileResponse(os.path.join(frontend_dir, 'profile.html'))

@app.get("/admin.html")
def serve_admin():
    return FileResponse(os.path.join(frontend_dir, 'admin.html'))

# Mount static directories
css_dir = os.path.join(frontend_dir, 'css')
js_dir = os.path.join(frontend_dir, 'js')
icons_dir = os.path.join(frontend_dir, 'icons')

if os.path.isdir(css_dir):
    app.mount('/css', StaticFiles(directory=css_dir), name='css')
if os.path.isdir(js_dir):
    app.mount('/js', StaticFiles(directory=js_dir), name='js')
if os.path.isdir(icons_dir):
    app.mount('/icons', StaticFiles(directory=icons_dir), name='icons')

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(frontend_dir, 'index.html'))

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'
    uvicorn.run("backend.app:app", host=host, port=port, reload=debug)
