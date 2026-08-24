from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.chatbot import ask_chatbot


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/chatbot",
    tags=["AI Chatbot"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# CHAT ENDPOINT
# ============================================================

@router.post("/chat")
def chat(
    data: ChatRequest,
):

    message = data.message.strip()

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    if len(message) > 2000:

        raise HTTPException(
            status_code=400,
            detail="Message is too long.",
        )

    try:

        reply = ask_chatbot(
            message
        )

        return {
            "message": message,
            "reply": reply,
        }

    except Exception as error:

        print(
            "Chatbot API error:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Could not process chatbot request.",
        )