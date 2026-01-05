# utils/pdf_converter.py
"""
Markdown转PDF转换器
支持中文字体、表格渲染、专业排版
"""

import os
import tempfile
from datetime import datetime
from typing import Optional

# 尝试导入PDF生成库
try:
    from weasyprint import HTML, CSS
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False

try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


def get_pdf_css() -> str:
    """
    获取PDF样式表
    专业金融研报风格
    """
    return """
    @page {
        size: A4;
        margin: 2cm 2.5cm;
        @top-center {
            content: "FinSight AI 行业研究报告";
            font-size: 9pt;
            color: #666;
        }
        @bottom-center {
            content: "第 " counter(page) " 页";
            font-size: 9pt;
            color: #666;
        }
    }
    
    body {
        font-family: "Noto Sans SC", "Microsoft YaHei", "SimHei", sans-serif;
        font-size: 11pt;
        line-height: 1.8;
        color: #333;
        text-align: justify;
    }
    
    h1 {
        font-size: 22pt;
        font-weight: 700;
        color: #1a365d;
        text-align: center;
        margin-top: 0;
        margin-bottom: 1.5em;
        padding-bottom: 0.5em;
        border-bottom: 3px solid #2563eb;
    }
    
    h2 {
        font-size: 16pt;
        font-weight: 600;
        color: #1e40af;
        margin-top: 1.5em;
        margin-bottom: 0.8em;
        padding-bottom: 0.3em;
        border-bottom: 2px solid #3b82f6;
        page-break-after: avoid;
    }
    
    h3 {
        font-size: 13pt;
        font-weight: 600;
        color: #1e3a8a;
        margin-top: 1.2em;
        margin-bottom: 0.6em;
        page-break-after: avoid;
    }
    
    h4 {
        font-size: 12pt;
        font-weight: 600;
        color: #1e40af;
        margin-top: 1em;
        margin-bottom: 0.5em;
    }
    
    p {
        margin-bottom: 0.8em;
        text-indent: 2em;
    }
    
    /* 表格样式 - 专业金融风格 */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1.5em 0;
        font-size: 10pt;
        page-break-inside: avoid;
    }
    
    th {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        font-weight: 600;
        padding: 10px 12px;
        text-align: left;
        border: 1px solid #1e40af;
    }
    
    td {
        padding: 8px 12px;
        border: 1px solid #e5e7eb;
        vertical-align: top;
    }
    
    tr:nth-child(even) {
        background-color: #f8fafc;
    }
    
    tr:hover {
        background-color: #eff6ff;
    }
    
    /* 列表样式 */
    ul, ol {
        margin: 0.8em 0;
        padding-left: 2em;
    }
    
    li {
        margin-bottom: 0.4em;
        text-indent: 0;
    }
    
    /* 引用块 */
    blockquote {
        border-left: 4px solid #3b82f6;
        padding: 0.5em 1em;
        margin: 1em 0;
        background-color: #eff6ff;
        color: #1e40af;
        font-style: italic;
    }
    
    /* 代码块 */
    code {
        background-color: #f1f5f9;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: "JetBrains Mono", "Consolas", monospace;
        font-size: 0.9em;
    }
    
    pre {
        background-color: #1e293b;
        color: #e2e8f0;
        padding: 1em;
        border-radius: 6px;
        overflow-x: auto;
        font-size: 9pt;
    }
    
    pre code {
        background: none;
        padding: 0;
        color: inherit;
    }
    
    /* 强调文本 */
    strong {
        color: #1e40af;
        font-weight: 600;
    }
    
    em {
        color: #475569;
    }
    
    /* 链接 */
    a {
        color: #2563eb;
        text-decoration: none;
    }
    
    /* 分割线 */
    hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 2em 0;
    }
    
    /* 封面页样式 */
    .cover-page {
        text-align: center;
        padding-top: 30%;
        page-break-after: always;
    }
    
    .cover-title {
        font-size: 28pt;
        font-weight: 700;
        color: #1e40af;
        margin-bottom: 0.5em;
    }
    
    .cover-subtitle {
        font-size: 14pt;
        color: #64748b;
        margin-bottom: 2em;
    }
    
    .cover-info {
        font-size: 11pt;
        color: #475569;
        margin-top: 3em;
    }
    
    /* 目录样式 */
    .toc {
        page-break-after: always;
    }
    
    .toc h2 {
        text-align: center;
        border-bottom: none;
    }
    
    .toc ul {
        list-style: none;
        padding-left: 0;
    }
    
    .toc li {
        margin-bottom: 0.5em;
        border-bottom: 1px dotted #ccc;
        padding-bottom: 0.3em;
    }
    
    /* 风险提示框 */
    .risk-warning {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-left: 4px solid #f59e0b;
        padding: 1em;
        margin: 1em 0;
        border-radius: 4px;
    }
    
    /* 重要结论框 */
    .key-finding {
        background-color: #dbeafe;
        border: 1px solid #3b82f6;
        border-left: 4px solid #3b82f6;
        padding: 1em;
        margin: 1em 0;
        border-radius: 4px;
    }
    
    /* 页面分隔 */
    .page-break {
        page-break-before: always;
    }
    """


def markdown_to_html(md_content: str, title: str = "行业研究报告") -> str:
    """
    将Markdown转换为HTML
    """
    if not HAS_MARKDOWN:
        # 简单的Markdown转换
        html_content = md_content
        html_content = html_content.replace('\n\n', '</p><p>')
        html_content = html_content.replace('\n', '<br>')
        html_content = f'<p>{html_content}</p>'
    else:
        # 使用markdown库转换
        md = markdown.Markdown(
            extensions=[
                'tables',
                'fenced_code',
                'toc',
                'nl2br',
                'sane_lists'
            ]
        )
        html_content = md.convert(md_content)
    
    # 构建完整HTML文档
    html_doc = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return html_doc


def convert_md_to_pdf(
    md_content: str,
    output_path: Optional[str] = None,
    title: str = "行业研究报告",
    add_cover: bool = True,
    province: str = "",
    industry: str = "",
    year: str = ""
) -> bytes:
    """
    将Markdown内容转换为PDF
    
    Args:
        md_content: Markdown文本内容
        output_path: 输出文件路径（可选）
        title: 报告标题
        add_cover: 是否添加封面
        province: 省份
        industry: 行业
        year: 年份
    
    Returns:
        PDF文件的字节内容
    """
    if not HAS_WEASYPRINT:
        raise ImportError("需要安装weasyprint库: pip install weasyprint")
    
    # 构建封面
    cover_html = ""
    if add_cover:
        report_title = f"{year}年{province}{industry}行业研究报告" if province and industry else title
        cover_html = f"""
        <div class="cover-page">
            <div class="cover-title">{report_title}</div>
            <div class="cover-subtitle">深度行业研究报告</div>
            <div class="cover-info">
                <p>FinSight AI Agent</p>
                <p>报告日期：{datetime.now().strftime('%Y年%m月%d日')}</p>
                <p style="margin-top: 2em; font-size: 9pt; color: #94a3b8;">
                    本报告由AI智能体自动生成，仅供参考
                </p>
            </div>
        </div>
        """
    
    # 转换Markdown为HTML
    html_content = markdown_to_html(md_content, title)
    
    # 在body开头插入封面
    if add_cover:
        html_content = html_content.replace('<body>', f'<body>{cover_html}')
    
    # 获取CSS样式
    css = CSS(string=get_pdf_css())
    
    # 生成PDF
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf(stylesheets=[css])
    
    # 如果指定了输出路径，保存文件
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
    
    return pdf_bytes


def convert_md_file_to_pdf(
    md_file_path: str,
    output_path: Optional[str] = None,
    **kwargs
) -> bytes:
    """
    将Markdown文件转换为PDF
    
    Args:
        md_file_path: Markdown文件路径
        output_path: 输出PDF文件路径（可选，默认同名.pdf）
        **kwargs: 传递给convert_md_to_pdf的其他参数
    
    Returns:
        PDF文件的字节内容
    """
    # 读取Markdown文件
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 如果没有指定输出路径，使用同名.pdf
    if not output_path:
        output_path = md_file_path.rsplit('.', 1)[0] + '.pdf'
    
    # 从文件名提取信息
    filename = os.path.basename(md_file_path)
    parts = filename.replace('.md', '').split('_')
    
    # 尝试解析文件名中的年份、省份、行业
    year = kwargs.get('year', '')
    province = kwargs.get('province', '')
    industry = kwargs.get('industry', '')
    
    if len(parts) >= 3 and not year:
        year = parts[0] if parts[0].isdigit() else ''
    if len(parts) >= 3 and not province:
        province = parts[1] if '省' in parts[1] or '市' in parts[1] else ''
    if len(parts) >= 3 and not industry:
        industry = parts[2] if parts[2] else ''
    
    return convert_md_to_pdf(
        md_content=md_content,
        output_path=output_path,
        year=year,
        province=province,
        industry=industry,
        **kwargs
    )


# 简化的备用方案（不依赖weasyprint）
def simple_md_to_pdf(md_content: str, output_path: str) -> bool:
    """
    简化的Markdown转PDF方案
    使用系统命令行工具
    """
    try:
        # 创建临时HTML文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            html = markdown_to_html(md_content)
            # 添加内联样式
            styled_html = html.replace('<head>', f'<head><style>{get_pdf_css()}</style>')
            f.write(styled_html)
            temp_html = f.name
        
        # 尝试使用manus-md-to-pdf命令
        import subprocess
        result = subprocess.run(
            ['manus-md-to-pdf', temp_html, output_path],
            capture_output=True,
            text=True
        )
        
        # 清理临时文件
        os.unlink(temp_html)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"PDF转换失败: {e}")
        return False


if __name__ == "__main__":
    # 测试代码
    test_md = """
# 测试报告

## 第一章 概述

这是一个测试段落。

### 1.1 背景

| 指标 | 数值 | 说明 |
|------|------|------|
| 市场规模 | 1000亿 | 2024年 |
| 增长率 | 15% | 年均 |

## 第二章 分析

**重要结论**：这是一个重要的发现。

- 要点1
- 要点2
- 要点3
    """
    
    try:
        pdf_bytes = convert_md_to_pdf(
            test_md,
            output_path="test_report.pdf",
            title="测试报告",
            province="浙江省",
            industry="人工智能",
            year="2025"
        )
        print(f"PDF生成成功，大小: {len(pdf_bytes)} bytes")
    except Exception as e:
        print(f"PDF生成失败: {e}")
