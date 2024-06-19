from pydantic import BaseModel
from typing import List, Optional


class TaskData(BaseModel):
    target_url: str
    method: str
    post_body: Optional[dict] = None
    header: Optional[dict] = None
    frequency: int = 10
    times: int
    arrData: Optional[List[str]] = None
    callback_url: Optional[str] = None


class TaskId(BaseModel):
    task_id: int
