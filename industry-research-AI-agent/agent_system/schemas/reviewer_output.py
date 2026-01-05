from typing import List, Optional
from pydantic import BaseModel, Field

class RevisionTask(BaseModel):
    chapter: str = Field(..., description="需要修改的章节标题")
    section: Optional[str] = Field(None, description="需要修改的小节")
    issue: str = Field(..., description="存在的问题说明")
    rewrite_requirement: str = Field(..., description="具体的补写指令")

class ReviewerOutput(BaseModel):
    need_revision: bool = Field(False, description="是否需要触发局部补写机制")
    revision_tasks: List[RevisionTask] = Field(default_factory=list, description="具体的修改任务列表")