# agent_system/schemas/reviewer_output.py
"""
Reviewer输出数据模型 - 增强版
核心改进：
1. 增加字段验证器，处理各种LLM输出格式
2. 提供默认值，确保模型始终可用
3. 支持多种字段名称（兼容不同LLM输出习惯）
"""
from typing import List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class RevisionTask(BaseModel):
    """单个修改任务"""
    chapter: str = Field(default="全文/未知章节", description="需要修改的章节标题")
    section: Optional[str] = Field(default=None, description="需要修改的小节")
    issue: str = Field(default="需要改进", description="存在的问题说明")
    rewrite_requirement: str = Field(default="请根据专家意见进行针对性补充与修改。", description="具体的补写指令")
    
    @field_validator('chapter', mode='before')
    @classmethod
    def validate_chapter(cls, v: Any) -> str:
        if v is None or v == '':
            return "全文/未知章节"
        return str(v).strip()
    
    @field_validator('section', mode='before')
    @classmethod
    def validate_section(cls, v: Any) -> Optional[str]:
        if v is None or v == '' or v == 'null' or v == 'None':
            return None
        return str(v).strip()
    
    @field_validator('issue', mode='before')
    @classmethod
    def validate_issue(cls, v: Any) -> str:
        if v is None or v == '':
            return "需要改进"
        return str(v).strip()
    
    @field_validator('rewrite_requirement', mode='before')
    @classmethod
    def validate_rewrite_requirement(cls, v: Any) -> str:
        if v is None or v == '':
            return "请根据专家意见进行针对性补充与修改。"
        return str(v).strip()
    
    class Config:
        # 允许额外字段，增加兼容性
        extra = 'ignore'
        # 允许从属性名或别名创建
        populate_by_name = True


class ReviewerOutput(BaseModel):
    """
    Reviewer Agent的结构化输出
    
    核心字段：
    - need_revision: 是否需要触发局部补写机制
    - revision_tasks: 具体的修改任务列表
    """
    need_revision: bool = Field(default=False, description="是否需要触发局部补写机制")
    revision_tasks: List[RevisionTask] = Field(default_factory=list, description="具体的修改任务列表")
    
    @field_validator('need_revision', mode='before')
    @classmethod
    def validate_need_revision(cls, v: Any) -> bool:
        """
        将各种可能的输入转换为布尔值
        处理LLM可能输出的各种格式
        """
        if isinstance(v, bool):
            return v
        
        if isinstance(v, str):
            # 清理字符串
            cleaned = v.strip().lower().strip('"\'')
            # 处理各种可能的true表示
            if cleaned in ('true', 'yes', '是', '需要', '1', 'need', 'required', '需修改'):
                return True
            # 处理各种可能的false表示
            if cleaned in ('false', 'no', '否', '不需要', '0', 'none', 'not required', '无需修改'):
                return False
            # 默认返回False
            return False
        
        if isinstance(v, (int, float)):
            return bool(v)
        
        # 其他情况返回False
        return False
    
    @field_validator('revision_tasks', mode='before')
    @classmethod
    def validate_revision_tasks(cls, v: Any) -> List[dict]:
        """
        验证并规范化revision_tasks列表
        """
        if v is None:
            return []
        
        if not isinstance(v, list):
            # 如果是单个dict，包装成列表
            if isinstance(v, dict):
                return [v]
            return []
        
        # 过滤掉无效项
        valid_tasks = []
        for item in v:
            if isinstance(item, dict):
                valid_tasks.append(item)
            elif isinstance(item, RevisionTask):
                valid_tasks.append(item.model_dump())
        
        return valid_tasks
    
    @model_validator(mode='after')
    def ensure_consistency(self) -> 'ReviewerOutput':
        """
        确保数据一致性：
        - 如果有revision_tasks但need_revision为False，自动设为True
        - 如果need_revision为True但没有revision_tasks，保持原样（可能是规则匹配结果）
        """
        if self.revision_tasks and len(self.revision_tasks) > 0 and not self.need_revision:
            # 有任务但标记为不需要修改，修正为需要修改
            object.__setattr__(self, 'need_revision', True)
        return self
    
    class Config:
        # 允许额外字段，增加兼容性
        extra = 'ignore'
        # 允许从属性名或别名创建
        populate_by_name = True
    
    @classmethod
    def safe_create(cls, data: Any) -> 'ReviewerOutput':
        """
        安全创建ReviewerOutput实例
        即使数据格式有问题也能返回有效对象
        """
        try:
            if isinstance(data, cls):
                return data
            if isinstance(data, dict):
                return cls(**data)
            if isinstance(data, str):
                # 尝试解析JSON字符串
                import json
                parsed = json.loads(data)
                return cls(**parsed)
            # 其他情况返回默认值
            return cls()
        except Exception as e:
            print(f"⚠️ [ReviewerOutput] 创建失败: {e}，返回默认值")
            return cls()


# 兼容性别名
ReviewOutput = ReviewerOutput
