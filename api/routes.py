from fastapi import APIRouter

from api.schemas import ChatRequest, ChatResponse
from utils.chat import ChatBot

router = APIRouter(prefix="/chat", tags=["Chat"])

bot = ChatBot()


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = bot.ask(request.question)

    return ChatResponse(answer=answer)