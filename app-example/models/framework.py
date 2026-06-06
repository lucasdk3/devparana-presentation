from pydantic import BaseModel
from typing import Optional

class Framework(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
