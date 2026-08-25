from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine

from app.models import (
    User,
    Item,
    Claim,
    Notification,
    AIMatch,
)

from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.items import router as items_router
from app.routes.claims import router as claims_router
from app.routes.notifications import (
    router as notifications_router,
)
from app.routes.realtime import (
    router as realtime_router,
)
from app.routes.ai import (
    router as ai_router,
)
from app.routes import contact
from app.routes.chatbot import router as chatbot_router
# from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="ReFindX API",
    description="AI Powered Lost & Found Platform",
    version="1.0.0",
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "https://refindx-frontend.onrender.com",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://refindx-frontend.onrender.com",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/uploads",
    StaticFiles(
        directory="uploads"
    ),
    name="uploads",
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(items_router)
app.include_router(claims_router)
app.include_router(notifications_router)
app.include_router(realtime_router)
app.include_router(ai_router)
app.include_router(
    contact.router
)

app.include_router(
    chatbot_router
)



# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Welcome to ReFindX API",
        "status": "running",
        "ai_matching": "enabled",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }