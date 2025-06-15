from pydantic import BaseModel


class FAQQuery(BaseModel):
    query: str


class FAQAnswer(BaseModel):
    question: str
    answer: str
