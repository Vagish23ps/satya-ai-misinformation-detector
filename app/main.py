from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import text

app = FastAPI(
    title="SATYA - Truth Detection Platform",
    description="AI-powered misinformation detection",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(text.router, prefix="/api/text", tags=["Text Analysis"])

@app.get("/")
def root():
    return {"message": "SATYA API is running 🔥", "status": "active"}
@app.get("/health")
def health_check():
    return {"status": "online", "version": "2.0"}