from fastapi import FastAPI

from .auth import router as auth_router
from .db import Base, engine

# Fine for development. For production, manage the schema with Alembic migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Email verification demo")
app.include_router(auth_router)

# If your frontend is on a different origin, add CORS:
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(CORSMiddleware, allow_origins=["https://your-frontend.com"],
#                    allow_methods=["*"], allow_headers=["*"])
