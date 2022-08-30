from pydantic import BaseModel


class StudyChangeState(BaseModel):
    uid: str
    state: bool = True
