# 用于 Agent 行为可观测（Manus 风格）
from datetime import datetime
from typing import List, Dict

# 全局日志缓冲区（单进程安全）
LOG_BUFFER: List[Dict] = []


def log_event(
    agent: str,
    action: str,
    content: str,
    level: str = "info"
):
    """
    记录 Agent 的一次行为
    """
    LOG_BUFFER.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "action": action,
        "content": content,
        "level": level
    })


def get_logs() -> List[Dict]:
    """
    前端轮询读取
    """
    return LOG_BUFFER


def clear_logs():
    """
    每次新任务开始前调用
    """
    LOG_BUFFER.clear()
