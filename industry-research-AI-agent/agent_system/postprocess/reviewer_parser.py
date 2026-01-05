# agent_system/postprocess/reviewer_parser.py
"""
Reviewer输出解析器 - 增强版
核心改进：
1. 多策略JSON提取（代码块、正则、启发式）
2. 字段类型强制转换与容错
3. 绝对保底机制，确保永远返回有效结构
"""
import json
import re
from typing import Dict, Any, List, Optional


def _safe_bool(value: Any) -> bool:
    """
    安全地将任意值转换为布尔类型
    处理各种可能的LLM输出格式
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        # 清理字符串
        cleaned = value.strip().lower().strip('"\'')
        # 处理各种可能的true表示
        if cleaned in ('true', 'yes', '是', '需要', '1', 'need', 'required'):
            return True
        # 处理各种可能的false表示
        if cleaned in ('false', 'no', '否', '不需要', '0', 'none', 'not required'):
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def _clean_json_string(json_str: str) -> str:
    """
    清理JSON字符串中的常见问题
    """
    if not json_str:
        return json_str
    
    # 去除可能的BOM和特殊字符
    json_str = json_str.strip()
    if json_str.startswith('\ufeff'):
        json_str = json_str[1:]
    
    # 去除末尾逗号
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*\]', ']', json_str)
    
    # 处理单引号（某些LLM可能输出单引号JSON）
    # 注意：这是简单处理，复杂情况可能需要更精细的逻辑
    if "'" in json_str and '"' not in json_str:
        json_str = json_str.replace("'", '"')
    
    # 处理换行符在字符串值中的问题
    json_str = re.sub(r'(?<!\\)\n(?=\s*["\'])', '', json_str)
    
    return json_str


def _extract_json_from_markdown(text: str) -> List[str]:
    """
    从Markdown代码块中提取JSON
    支持多种代码块格式
    """
    candidates = []
    
    # 策略1: ```json ... ``` 格式
    pattern1 = r"```json\s*([\s\S]*?)```"
    matches1 = re.findall(pattern1, text, re.IGNORECASE)
    candidates.extend(matches1)
    
    # 策略2: ``` ... ``` 格式（无语言标记）
    pattern2 = r"```\s*(\{[\s\S]*?\})\s*```"
    matches2 = re.findall(pattern2, text)
    candidates.extend(matches2)
    
    # 策略3: 【局部补写指令 JSON】后的代码块
    pattern3 = r"【局部补写指令\s*JSON】[^\{]*(\{[\s\S]*?\})"
    matches3 = re.findall(pattern3, text)
    candidates.extend(matches3)
    
    return candidates


def _extract_json_by_braces(text: str) -> List[str]:
    """
    通过花括号匹配提取可能的JSON对象
    使用栈来处理嵌套
    """
    candidates = []
    i = 0
    while i < len(text):
        if text[i] == '{':
            # 找到开始位置，使用栈来匹配
            stack = 1
            start = i
            i += 1
            while i < len(text) and stack > 0:
                if text[i] == '{':
                    stack += 1
                elif text[i] == '}':
                    stack -= 1
                i += 1
            if stack == 0:
                candidates.append(text[start:i])
        else:
            i += 1
    return candidates


def _validate_revision_task(task: Dict) -> Optional[Dict]:
    """
    验证并规范化单个revision_task
    """
    if not isinstance(task, dict):
        return None
    
    # 必须字段检查
    chapter = task.get('chapter', task.get('章节', ''))
    issue = task.get('issue', task.get('问题', task.get('问题说明', '')))
    rewrite_req = task.get('rewrite_requirement', task.get('补写要求', task.get('修改要求', '')))
    
    if not chapter and not issue:
        return None
    
    return {
        "chapter": str(chapter) if chapter else "全文/未知章节",
        "section": str(task.get('section', task.get('小节', ''))) if task.get('section', task.get('小节')) else None,
        "issue": str(issue) if issue else "需要改进",
        "rewrite_requirement": str(rewrite_req) if rewrite_req else "请根据专家意见进行针对性补充与修改。"
    }


def _parse_json_candidate(json_str: str) -> Optional[Dict]:
    """
    尝试解析单个JSON候选字符串
    """
    try:
        cleaned = _clean_json_string(json_str)
        data = json.loads(cleaned)
        
        if not isinstance(data, dict):
            return None
        
        # 检查是否包含reviewer相关字段
        has_need_revision = 'need_revision' in data or 'needRevision' in data or '需要修改' in data
        has_revision_tasks = 'revision_tasks' in data or 'revisionTasks' in data or '修改任务' in data
        
        if has_need_revision or has_revision_tasks:
            return data
        
        return None
    except json.JSONDecodeError:
        return None


def _extract_from_text_rules(text: str) -> Dict[str, Any]:
    """
    基于规则从文本中提取审核结论
    当JSON解析全部失败时使用
    """
    result = {
        "need_revision": False,
        "revision_tasks": []
    }
    
    # 关键词判定
    negative_keywords = [
        "需修改", "不合格", "需要补充", "存在缺失", "重大缺陷",
        "需要修改", "建议修改", "必须修改", "需补写", "需要补写",
        "不通过", "未通过", "需改进", "存在问题"
    ]
    positive_keywords = [
        "无需修改", "通过", "合格", "完美", "达标",
        "全部合格", "可直接定稿", "质量优秀", "符合要求"
    ]
    
    # 取前1000个字符判断结论
    head_text = text[:1000]
    
    is_negative = any(k in head_text for k in negative_keywords)
    is_positive = any(k in head_text for k in positive_keywords)
    
    # 优先判断正面结论
    if is_positive and not is_negative:
        result["need_revision"] = False
        return result
    
    if is_negative:
        result["need_revision"] = True
        
        # 尝试提取具体的修改建议
        lines = text.split("\n")
        current_chapter = ""
        
        for line in lines:
            line = line.strip()
            
            # 检测章节标题
            chapter_match = re.match(r'^(?:第\s*[一二三四五六七八九十\d]+\s*章|[一二三四五六七八九十\d]+[.、])\s*(.+)', line)
            if chapter_match:
                current_chapter = chapter_match.group(0)
                continue
            
            # 提取以 - 或 数字开头的建议行
            if (line.startswith("-") or line.startswith("•") or re.match(r'^\d+[.、)]', line)):
                # 排除无意义的标题行
                skip_keywords = ["问题清单", "修改建议", "评分", "审核维度", "检查项"]
                if any(k in line for k in skip_keywords):
                    continue
                
                if len(line) > 10:
                    result["revision_tasks"].append({
                        "chapter": current_chapter if current_chapter else "全文/未知章节",
                        "section": "",
                        "issue": line.lstrip('-•').strip(),
                        "rewrite_requirement": "请根据专家意见进行针对性补充与修改。"
                    })
    
    return result


def parse_reviewer_output(text: str) -> Dict[str, Any]:
    """
    解析 Reviewer 输出，提取是否需要修改 & 局部补写任务
    
    【核心改进】：
    1. 多策略JSON提取（Markdown代码块、正则匹配、花括号匹配）
    2. 字段类型强制转换与容错（处理各种LLM输出格式）
    3. 绝对保底机制，确保永远返回包含 'need_revision' 的字典
    
    Args:
        text: Reviewer Agent的原始输出文本
        
    Returns:
        Dict包含:
        - need_revision: bool, 是否需要修改
        - revision_tasks: List[Dict], 具体修改任务列表
    """
    
    # 1. 定义绝对保底的默认结构
    safe_result = {
        "need_revision": False,
        "revision_tasks": []
    }

    if not text:
        print("⚠️ [Reviewer Parser] 输入为空，返回默认值")
        return safe_result

    # 清理输入
    text = text.strip()
    
    # =======================================================
    # 策略 A: 优先提取 Markdown 代码块中的JSON
    # =======================================================
    candidate_jsons = _extract_json_from_markdown(text)
    
    # =======================================================
    # 策略 B: 如果没有代码块，尝试花括号匹配
    # =======================================================
    if not candidate_jsons:
        candidate_jsons = _extract_json_by_braces(text)
    
    # =======================================================
    # 策略 C: 遍历所有候选者，解析并验证
    # =======================================================
    for json_str in candidate_jsons:
        data = _parse_json_candidate(json_str)
        if data:
            # 提取 need_revision 字段
            need_revision_value = (
                data.get("need_revision") or 
                data.get("needRevision") or 
                data.get("需要修改", False)
            )
            safe_result["need_revision"] = _safe_bool(need_revision_value)
            
            # 提取 revision_tasks 字段
            tasks_raw = (
                data.get("revision_tasks") or 
                data.get("revisionTasks") or 
                data.get("修改任务", [])
            )
            
            if isinstance(tasks_raw, list):
                for task in tasks_raw:
                    validated_task = _validate_revision_task(task)
                    if validated_task:
                        safe_result["revision_tasks"].append(validated_task)
            
            print(f"✅ [Reviewer Parser] JSON解析成功: need_revision={safe_result['need_revision']}, tasks={len(safe_result['revision_tasks'])}")
            return safe_result
    
    # =======================================================
    # 策略 D: JSON解析全部失败，转为规则匹配
    # =======================================================
    print(f"⚠️ [Reviewer Parser] JSON解析失败，转为规则匹配")
    rule_result = _extract_from_text_rules(text)
    
    safe_result["need_revision"] = rule_result["need_revision"]
    safe_result["revision_tasks"] = rule_result["revision_tasks"]
    
    print(f"📋 [Reviewer Parser] 规则匹配结果: need_revision={safe_result['need_revision']}, tasks={len(safe_result['revision_tasks'])}")
    
    return safe_result


# 兼容性别名
def parse_review_output(text: str) -> Dict[str, Any]:
    """别名函数，保持向后兼容"""
    return parse_reviewer_output(text)
