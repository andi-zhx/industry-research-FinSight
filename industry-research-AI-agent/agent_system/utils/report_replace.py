import re

def replace_chapter(report_text: str, chapter_title: str, new_content: str) -> str:
    """
    用 new_content 替换 report_text 中对应章节（按章节标题）
    """

    # 匹配：## 第X章 标题  到  下一个 ## 第Y章 或 EOF
    pattern = rf"(##\s*{re.escape(chapter_title)}[\s\S]*?)(?=\n##\s*第\d+章|\Z)"

    match = re.search(pattern, report_text)
    if not match:
        # 找不到就兜底：直接追加（但打 warning）
        print(f"⚠️ 未找到章节 {chapter_title}，已追加到文末")
        return report_text + "\n\n" + new_content

    return re.sub(pattern, new_content, report_text, count=1)