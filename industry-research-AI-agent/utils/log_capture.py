# utils/log_capture.py
"""
实时日志捕获模块
用于在Streamlit前端实时显示后台运行日志
"""
import sys
import io
import threading
import queue
import time
from typing import Optional, Callable
from contextlib import contextmanager


class LogCapture:
    """
    日志捕获器
    捕获stdout和stderr输出，支持实时回调
    """
    
    def __init__(self):
        self.log_queue = queue.Queue()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.capturing = False
        self._lock = threading.Lock()
        
    def start(self):
        """开始捕获日志"""
        with self._lock:
            if self.capturing:
                return
            self.capturing = True
            self._captured_stdout = _StreamCapture(self.log_queue, self.original_stdout, "[INFO]")
            self._captured_stderr = _StreamCapture(self.log_queue, self.original_stderr, "[ERROR]")
            sys.stdout = self._captured_stdout
            sys.stderr = self._captured_stderr
    
    def stop(self):
        """停止捕获日志"""
        with self._lock:
            if not self.capturing:
                return
            self.capturing = False
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
    
    def get_logs(self, max_lines: int = 100) -> list:
        """获取捕获的日志"""
        logs = []
        try:
            while not self.log_queue.empty() and len(logs) < max_lines:
                logs.append(self.log_queue.get_nowait())
        except queue.Empty:
            pass
        return logs
    
    def clear(self):
        """清空日志队列"""
        try:
            while not self.log_queue.empty():
                self.log_queue.get_nowait()
        except queue.Empty:
            pass


class _StreamCapture(io.StringIO):
    """
    流捕获器
    同时写入队列和原始流
    """
    
    def __init__(self, log_queue: queue.Queue, original_stream, prefix: str = ""):
        super().__init__()
        self.log_queue = log_queue
        self.original_stream = original_stream
        self.prefix = prefix
        self._buffer = ""
        
    def write(self, text: str):
        # 写入原始流（保持控制台输出）
        if self.original_stream:
            self.original_stream.write(text)
            self.original_stream.flush()
        
        # 缓冲并按行分割
        self._buffer += text
        while '\n' in self._buffer:
            line, self._buffer = self._buffer.split('\n', 1)
            if line.strip():  # 忽略空行
                timestamp = time.strftime("%H:%M:%S")
                formatted_line = f"[{timestamp}] {line}"
                self.log_queue.put(formatted_line)
        
        return len(text)
    
    def flush(self):
        if self.original_stream:
            self.original_stream.flush()


# 全局日志捕获器实例
_global_log_capture: Optional[LogCapture] = None


def get_log_capture() -> LogCapture:
    """获取全局日志捕获器"""
    global _global_log_capture
    if _global_log_capture is None:
        _global_log_capture = LogCapture()
    return _global_log_capture


@contextmanager
def capture_logs():
    """
    上下文管理器：捕获代码块中的日志
    
    Usage:
        with capture_logs() as log_capture:
            # 执行代码
            pass
        logs = log_capture.get_logs()
    """
    log_capture = get_log_capture()
    log_capture.clear()
    log_capture.start()
    try:
        yield log_capture
    finally:
        log_capture.stop()


class StreamlitLogDisplay:
    """
    Streamlit日志显示组件
    在Streamlit界面中实时显示日志
    """
    
    def __init__(self, container, max_lines: int = 50):
        """
        初始化日志显示组件
        
        Args:
            container: Streamlit容器（如st.empty()或st.container()）
            max_lines: 最大显示行数
        """
        self.container = container
        self.max_lines = max_lines
        self.logs = []
        self.log_capture = get_log_capture()
        
    def update(self):
        """更新日志显示"""
        new_logs = self.log_capture.get_logs()
        self.logs.extend(new_logs)
        
        # 保持最大行数
        if len(self.logs) > self.max_lines:
            self.logs = self.logs[-self.max_lines:]
        
        # 格式化日志显示
        if self.logs:
            log_text = self._format_logs()
            self.container.markdown(f"""
            <div class="log-container" style="
                background-color: #0D1117;
                border: 1px solid #30363D;
                border-radius: 8px;
                padding: 1rem;
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                font-size: 0.85rem;
                max-height: 400px;
                overflow-y: auto;
                color: #E6EDF3;
            ">
                <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{log_text}</pre>
            </div>
            """, unsafe_allow_html=True)
    
    def _format_logs(self) -> str:
        """格式化日志文本，添加颜色标记"""
        formatted_lines = []
        for line in self.logs:
            # 根据内容添加颜色
            if "✅" in line or "成功" in line or "完成" in line:
                color = "#3FB950"  # 绿色
            elif "⚠️" in line or "警告" in line or "Warning" in line.lower():
                color = "#D29922"  # 黄色
            elif "❌" in line or "错误" in line or "Error" in line.lower() or "失败" in line:
                color = "#F85149"  # 红色
            elif "🔍" in line or "📋" in line or "📊" in line:
                color = "#58A6FF"  # 蓝色
            elif "Phase" in line:
                color = "#A371F7"  # 紫色
            else:
                color = "#E6EDF3"  # 默认白色
            
            formatted_lines.append(f'<span style="color: {color};">{self._escape_html(line)}</span>')
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def _escape_html(text: str) -> str:
        """转义HTML特殊字符"""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;"))
    
    def clear(self):
        """清空日志"""
        self.logs = []
        self.log_capture.clear()
