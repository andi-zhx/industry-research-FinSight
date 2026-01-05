# agent_system/postprocess/reviewer_parser.py
"""
Reviewer输出解析器 - 稳定版
核心改进：
1. 完全基于规则匹配，不依赖JSON解析
2. 使用明确的标记词（REVIEW_RESULT, SCORE）
3. 多重保底机制，确保永远返回有效结构
"""
import re
from typing import Dict, Any, List, Tuple


def _extract_score(text: str) -> int:
    """
    从文本中提取评分
    支持多种格式：SCORE: 85/100, 评分：85分, 85/100等
    """
    # 策略1: 匹配 SCORE: XX/100 格式
    match = re.search(r'SCORE\s*[:：]\s*(\d+)\s*/\s*100', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    
    # 策略2: 匹配 报告质量评分：XX/100 格式
    match = re.search(r'(?:报告质量)?评分\s*[:：]\s*(\d+)\s*/\s*100', text)
    if match:
        return int(match.group(1))
    
    # 策略3: 匹配 XX/100 格式
    match = re.search(r'(\d+)\s*/\s*100', text)
    if match:
        return int(match.group(1))
    
    # 策略4: 匹配 XX分 格式
    match = re.search(r'(\d+)\s*分', text)
    if match:
        score = int(match.group(1))
        if 0 <= score <= 100:
            return score
    
    # 默认返回85分（通过）
    return 85


def _extract_review_result(text: str) -> bool:
    """
    从文本中提取审核结论
    返回True表示需要修改，False表示通过
    """
    text_upper = text.upper()
    
    # 策略1: 匹配 REVIEW_RESULT: PASS/NEED_REVISION
    if 'REVIEW_RESULT' in text_upper:
        if 'NEED_REVISION' in text_upper or 'NEED REVISION' in text_upper:
            return True
        if 'PASS' in text_upper:
            return False
    
    # 策略2: 匹配中文结论
    positive_keywords = [
        '通过', '合格', '可直接定稿', '无需修改', '质量优秀',
        '达标', '符合要求', '可以发布', '审核通过'
    ]
    negative_keywords = [
        '需修改', '不合格', '需要修改', '建议修改', '必须修改',
        '需补写', '需要补写', '不通过', '未通过', '需改进',
        '存在问题', '需要补充', '存在缺失', '重大缺陷'
    ]
    
    # 检查前500字符中的关键词
    head_text = text[:500]
    
    has_positive = any(k in head_text for k in positive_keywords)
    has_negative = any(k in head_text for k in negative_keywords)
    
    # 如果同时有正面和负面关键词，以负面为准
    if has_negative:
        return True
    if has_positive:
        return False
    
    # 默认返回False（通过）
    return False


def _extract_problem_chapters(text: str) -> List[Dict[str, str]]:
    """
    从审核文本中提取有问题的章节
    """
    problems = []
    
    # 匹配问题清单中的章节
    # 格式1: 第X章 XXX
    chapter_pattern = r'第\s*([一二三四五六七八九十\d]+)\s*章[：:\s]*([^\n]+)'
    matches = re.findall(chapter_pattern, text)
    for num, title in matches:
        problems.append({
            'chapter': f'第{num}章 {title.strip()}',
            'issue': '审核发现问题',
            'rewrite_requirement': '请根据审核意见进行修改和补充'
        })
    
    # 格式2: X.X XXX 小节
    section_pattern = r'(\d+\.\d+)\s+([^\n]+?)(?:存在|缺少|不足|需要)'
    matches = re.findall(section_pattern, text)
    for num, title in matches:
        problems.append({
            'chapter': f'{num} {title.strip()}',
            'issue': '审核发现问题',
            'rewrite_requirement': '请根据审核意见进行修改和补充'
        })
    
    # 格式3: 【问题】后面的内容
    problem_pattern = r'(?:问题|缺陷|不足)[：:\s]*([^\n]+)'
    matches = re.findall(problem_pattern, text)
    for problem in matches[:5]:  # 最多取5个
        if len(problem) > 10:
            problems.append({
                'chapter': '全文/未知章节',
                'issue': problem.strip(),
                'rewrite_requirement': '请根据审核意见进行修改和补充'
            })
    
    # 去重
    seen = set()
    unique_problems = []
    for p in problems:
        key = p['chapter']
        if key not in seen:
            seen.add(key)
            unique_problems.append(p)
    
    return unique_problems[:5]  # 最多返回5个问题


def parse_reviewer_output(text: str) -> Dict[str, Any]:
    """
    解析 Reviewer 输出，提取是否需要修改 & 问题列表
    
    【核心改进】：
    1. 完全基于规则匹配，不依赖JSON解析
    2. 使用明确的标记词（REVIEW_RESULT, SCORE）
    3. 多重保底机制，确保永远返回有效结构
    
    Args:
        text: Reviewer Agent的原始输出文本
        
    Returns:
        Dict包含:
        - need_revision: bool, 是否需要修改
        - score: int, 评分（0-100）
        - revision_tasks: List[Dict], 具体修改任务列表
    """
    
    # 定义绝对保底的默认结构
    safe_result = {
        "need_revision": False,
        "score": 85,
        "revision_tasks": []
    }

    if not text:
        print("⚠️ [Reviewer Parser] 输入为空，返回默认值")
        return safe_result

    # 清理输入
    text = text.strip()
    
    # 1. 提取评分
    score = _extract_score(text)
    safe_result["score"] = score
    print(f"📊 [Reviewer Parser] 提取评分: {score}/100")
    
    # 2. 提取审核结论
    need_revision = _extract_review_result(text)
    
    # 3. 根据评分调整结论
    # 如果评分低于85分，强制需要修改
    if score < 85:
        need_revision = True
    # 如果评分高于90分，强制通过
    elif score >= 90:
        need_revision = False
    
    safe_result["need_revision"] = need_revision
    print(f"📋 [Reviewer Parser] 审核结论: {'需要修改' if need_revision else '通过'}")
    
    # 4. 如果需要修改，提取问题章节
    if need_revision:
        problems = _extract_problem_chapters(text)
        safe_result["revision_tasks"] = problems
        print(f"📝 [Reviewer Parser] 提取问题章节: {len(problems)}个")
    
    return safe_result


def parse_review_output(text: str) -> Dict[str, Any]:
    """别名函数，保持向后兼容"""
    return parse_reviewer_output(text)


# ============================================================
# 辅助函数：从报告中提取指定章节内容
# ============================================================
def extract_chapter_content(report: str, chapter_title: str) -> str:
    """
    从报告中提取指定章节的内容
    
    Args:
        report: 完整报告文本
        chapter_title: 章节标题（支持模糊匹配）
        
    Returns:
        章节内容，如果未找到返回空字符串
    """
    lines = report.split('\n')
    content_lines = []
    in_chapter = False
    chapter_level = 0
    
    for line in lines:
        # 检测标题行
        if line.startswith('#'):
            # 计算标题级别
            level = len(re.match(r'^#+', line).group())
            title_text = line.lstrip('#').strip()
            
            # 检查是否是目标章节
            if chapter_title in title_text or title_text in chapter_title:
                in_chapter = True
                chapter_level = level
                content_lines.append(line)
                continue
            
            # 如果已经在章节中，检查是否遇到同级或更高级标题
            if in_chapter and level <= chapter_level:
                break
        
        if in_chapter:
            content_lines.append(line)
    
    return '\n'.join(content_lines)
