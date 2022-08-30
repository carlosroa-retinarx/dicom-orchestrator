from pydantic import BaseModel, ValidationError
from typing import List


class UidsPost(BaseModel):
    uids: List[str]

