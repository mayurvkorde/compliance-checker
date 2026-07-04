from langchain_openai import ChatOpenAI
from config.settings import get_settings

settings = get_settings()

_llm = ChatOpenAI(
    model="gpt-4o",
    api_key=settings.OPENAI_API_KEY,
    temperature=0,
    max_tokens=1200,
)

def get_llm():
    return _llm
