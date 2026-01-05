# agent_system/postprocess/reviewer_parser.py
import json
import re
from typing import Dict, Any

def parse_reviewer_output(text: str) -> Dict[str, Any]:
    """
    解析 Reviewer 输出，提取是否需要修改 & 局部补写任务
    【核心改进】：
    1. 优先匹配 Markdown 代码块 (```json ... ```)
    2. 使用非贪婪正则 + 循环匹配，找到第一个合法的 JSON 对象
    3. 绝对保底机制，确保永远返回包含 'need_revision' 的字典
    """
    
    # 1. 定义绝对保底的默认结构
    safe_result = {
        "need_revision": False,
        "revision_tasks": []
    }

    if not text:
        return safe_result

    # 清理可能的干扰字符
    text = text.strip()

    # =======================================================
    # 策略 A: 优先提取 Markdown 代码块 (```json ... ```)
    # =======================================================
    # 很多 LLM 会把 JSON 放在代码块里，这是最准确的
    code_block_pattern = r"```(?:json)?\s*(\{[\s\S]*?\})\s*```"
    code_blocks = re.findall(code_block_pattern, text, re.IGNORECASE)
    
    candidate_jsons = code_blocks # 先尝试代码块里的内容

    # =======================================================
    # 策略 B: 如果没代码块，尝试正则提取所有可能的 JSON 对象
    # =======================================================
    if not candidate_jsons:
        # 使用非贪婪匹配 (.*?) 寻找每一对 {}
        # 注意：这无法处理嵌套极深的复杂 JSON，但对 Reviewer 输出通常足够
        json_pattern = r"(\{[\s\S]*?\})"
        candidate_jsons = re.findall(json_pattern, text)

    # =======================================================
    # 验证与解析：遍历所有候选者，直到找到一个合法的
    # =======================================================
    for json_str in candidate_jsons:
        try:
            # 简单清洗
            json_str = re.sub(r',\s*\}', '}', json_str) # 去掉末尾逗号
            json_str = re.sub(r',\s*\]', ']', json_str)
            
            data = json.loads(json_str)
            
            if isinstance(data, dict):
                # 检查是否包含关键特征，防止匹配到 Prompt 里的示例 JSON
                # Reviewer 的真实输出通常包含 "need_revision" 且可能为 True/False
                # 即使没有 need_revision，只要是 dict 我们也认，之后补默认值
                
                # 合并数据到 safe_result
                if "need_revision" in data:
                    val = data["need_revision"]
                    if isinstance(val, bool):
                        safe_result["need_revision"] = val
                    elif isinstance(val, str):
                        safe_result["need_revision"] = val.lower() == "true"
                
                if "revision_tasks" in data and isinstance(data["revision_tasks"], list):
                    safe_result["revision_tasks"] = data["revision_tasks"]
                
                # 只要成功解析出一个包含 revision 信息的 JSON，就直接返回
                # 避免被后面匹配到的其他无效 JSON 覆盖
                if "need_revision" in data or "revision_tasks" in data:
                    return safe_result

        except json.JSONDecodeError:
            continue # 解析失败，尝试下一个候选者

    # =======================================================
    # 策略 C: 兜底规则解析 (如果 JSON 全挂了)
    # =======================================================
    print(f"⚠️ [Reviewer Parser] JSON 解析全部失败，转为规则匹配")
    
    # 关键词判定
    negative_keywords = ["需修改", "不合格", "需要补充", "存在缺失", "重大缺陷"]
    positive_keywords = ["无需修改", "通过", "合格", "完美"]
    
    # 取前 500 个字符判断结论（结论通常在开头）
    head_text = text[:500]
    
    is_negative = any(k in head_text for k in negative_keywords)
    is_positive = any(k in head_text for k in positive_keywords)
    
    # 如果既有"需修改"又有"无需修改"（较少见），偏向于无需
    if is_negative and not is_positive:
        safe_result["need_revision"] = True
        
        # 简单提取行级任务
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            # 提取以 - 或 数字开头的建议行
            if (line.startswith("-") or line.startswith("1.")) and len(line) > 10:
                # 排除掉无意义的标题行
                if "问题清单" in line or "修改建议" in line:
                    continue
                    
                safe_result["revision_tasks"].append({
                    "chapter": "全文/未知章节",
                    "section": "",
                    "issue": line,
                    "rewrite_requirement": "请根据专家意见进行针对性补充与修改。"
                })

    return safe_result