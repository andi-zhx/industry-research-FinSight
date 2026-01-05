# agent_system/tools/enhanced_pdf.py
"""
增强版PDF处理模块
改进切片策略，支持语义切分和表格提取

核心改进：
1. 语义切分 - 按段落和章节切分，而非固定长度
2. 表格提取 - 精确提取表格数据
3. 目录识别 - 自动识别文档结构
4. 元数据提取 - 提取标题、作者、日期等
"""

import os
import re
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


@dataclass
class PDFChunk:
    """PDF文档片段"""
    content: str
    chunk_type: str  # 'text', 'table', 'title', 'list'
    page_number: int
    section: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PDFStructure:
    """PDF文档结构"""
    title: str = ""
    author: str = ""
    date: str = ""
    total_pages: int = 0
    sections: List[Dict] = None
    tables: List[Dict] = None
    
    def __post_init__(self):
        if self.sections is None:
            self.sections = []
        if self.tables is None:
            self.tables = []


class SemanticChunker:
    """
    语义切分器
    按语义边界切分文档，而非固定长度
    """
    
    # 章节标题模式
    SECTION_PATTERNS = [
        r'^第[一二三四五六七八九十\d]+[章节部分]',  # 第一章、第1节
        r'^[一二三四五六七八九十]+[、.．]',  # 一、二、
        r'^\d+[、.．]\d*',  # 1. 1.1
        r'^[（(]\d+[)）]',  # (1) （1）
        r'^[A-Z][、.．]',  # A. B.
    ]
    
    # 段落分隔符
    PARAGRAPH_SEPARATORS = [
        '\n\n',
        '\n　　',  # 中文段落缩进
        '\n    ',  # 英文段落缩进
    ]
    
    def __init__(self, max_chunk_size: int = 800, min_chunk_size: int = 100):
        """
        初始化语义切分器
        
        Args:
            max_chunk_size: 最大片段大小
            min_chunk_size: 最小片段大小
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
    
    def chunk(self, text: str, page_number: int = 1) -> List[PDFChunk]:
        """
        语义切分文本
        
        Args:
            text: 待切分文本
            page_number: 页码
        
        Returns:
            List[PDFChunk]: 切分后的片段列表
        """
        chunks = []
        current_section = ""
        
        # 1. 首先按章节切分
        sections = self._split_by_sections(text)
        
        for section_title, section_content in sections:
            if section_title:
                current_section = section_title
            
            # 2. 在章节内按段落切分
            paragraphs = self._split_by_paragraphs(section_content)
            
            # 3. 合并小段落，拆分大段落
            merged_chunks = self._merge_and_split(paragraphs)
            
            for chunk_content in merged_chunks:
                if len(chunk_content.strip()) >= self.min_chunk_size:
                    chunk_type = self._detect_chunk_type(chunk_content)
                    chunks.append(PDFChunk(
                        content=chunk_content.strip(),
                        chunk_type=chunk_type,
                        page_number=page_number,
                        section=current_section
                    ))
        
        return chunks
    
    def _split_by_sections(self, text: str) -> List[Tuple[str, str]]:
        """按章节切分"""
        sections = []
        current_title = ""
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            is_title = False
            for pattern in self.SECTION_PATTERNS:
                if re.match(pattern, line.strip()):
                    # 保存之前的章节
                    if current_content:
                        sections.append((current_title, '\n'.join(current_content)))
                    current_title = line.strip()
                    current_content = []
                    is_title = True
                    break
            
            if not is_title:
                current_content.append(line)
        
        # 保存最后一个章节
        if current_content:
            sections.append((current_title, '\n'.join(current_content)))
        
        return sections if sections else [("", text)]
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """按段落切分"""
        # 尝试不同的分隔符
        for sep in self.PARAGRAPH_SEPARATORS:
            if sep in text:
                paragraphs = text.split(sep)
                if len(paragraphs) > 1:
                    return [p.strip() for p in paragraphs if p.strip()]
        
        # 如果没有明显的段落分隔，按句子切分
        sentences = re.split(r'[。！？\n]', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _merge_and_split(self, paragraphs: List[str]) -> List[str]:
        """合并小段落，拆分大段落"""
        result = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(para) > self.max_chunk_size:
                # 保存当前累积的内容
                if current_chunk:
                    result.append(current_chunk)
                    current_chunk = ""
                
                # 拆分大段落
                for i in range(0, len(para), self.max_chunk_size):
                    result.append(para[i:i + self.max_chunk_size])
            
            elif len(current_chunk) + len(para) > self.max_chunk_size:
                # 当前累积内容已满，保存并开始新的
                result.append(current_chunk)
                current_chunk = para
            
            else:
                # 合并小段落
                if current_chunk:
                    current_chunk += "\n" + para
                else:
                    current_chunk = para
        
        # 保存最后的内容
        if current_chunk:
            result.append(current_chunk)
        
        return result
    
    def _detect_chunk_type(self, content: str) -> str:
        """检测片段类型"""
        # 检测表格
        if '|' in content and content.count('|') > 3:
            return 'table'
        
        # 检测列表
        if re.match(r'^[\d•\-\*]', content.strip()):
            return 'list'
        
        # 检测标题
        if len(content) < 50 and not content.endswith('。'):
            for pattern in self.SECTION_PATTERNS:
                if re.match(pattern, content.strip()):
                    return 'title'
        
        return 'text'


class TableExtractor:
    """
    表格提取器
    从PDF中精确提取表格数据
    """
    
    def extract_tables(self, pdf_path: str) -> List[Dict]:
        """
        从PDF中提取所有表格
        
        Args:
            pdf_path: PDF文件路径
        
        Returns:
            List[Dict]: 表格列表
        """
        tables = []
        
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_tables = page.extract_tables()
                    
                    for table_idx, table in enumerate(page_tables):
                        if table and len(table) > 1:
                            # 清理表格数据
                            cleaned_table = self._clean_table(table)
                            
                            # 转换为Markdown格式
                            markdown = self._table_to_markdown(cleaned_table)
                            
                            tables.append({
                                "page": page_num,
                                "index": table_idx,
                                "rows": len(cleaned_table),
                                "cols": len(cleaned_table[0]) if cleaned_table else 0,
                                "data": cleaned_table,
                                "markdown": markdown
                            })
        
        except ImportError:
            print("⚠️ pdfplumber未安装，无法提取表格")
        except Exception as e:
            print(f"⚠️ 表格提取失败: {e}")
        
        return tables
    
    def _clean_table(self, table: List[List]) -> List[List[str]]:
        """清理表格数据"""
        cleaned = []
        for row in table:
            cleaned_row = []
            for cell in row:
                if cell is None:
                    cleaned_row.append("")
                else:
                    # 清理空白字符
                    cleaned_row.append(str(cell).strip().replace('\n', ' '))
            cleaned.append(cleaned_row)
        return cleaned
    
    def _table_to_markdown(self, table: List[List[str]]) -> str:
        """将表格转换为Markdown格式"""
        if not table:
            return ""
        
        lines = []
        
        # 表头
        header = table[0]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        
        # 数据行
        for row in table[1:]:
            # 确保列数一致
            while len(row) < len(header):
                row.append("")
            lines.append("| " + " | ".join(row[:len(header)]) + " |")
        
        return "\n".join(lines)


class EnhancedPDFProcessor:
    """
    增强版PDF处理器
    整合语义切分、表格提取、结构识别
    """
    
    def __init__(self):
        self.chunker = SemanticChunker()
        self.table_extractor = TableExtractor()
    
    def process(self, pdf_path: str) -> Dict[str, Any]:
        """
        处理PDF文件
        
        Args:
            pdf_path: PDF文件路径
        
        Returns:
            Dict: 处理结果
        """
        if not os.path.exists(pdf_path):
            return {"error": f"文件不存在: {pdf_path}"}
        
        result = {
            "file_path": pdf_path,
            "file_name": os.path.basename(pdf_path),
            "structure": PDFStructure(),
            "chunks": [],
            "tables": [],
            "full_text": ""
        }
        
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                result["structure"].total_pages = len(pdf.pages)
                
                all_text = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # 提取文本
                    text = page.extract_text() or ""
                    all_text.append(text)
                    
                    # 语义切分
                    chunks = self.chunker.chunk(text, page_num)
                    result["chunks"].extend(chunks)
                
                result["full_text"] = "\n\n".join(all_text)
            
            # 提取表格
            result["tables"] = self.table_extractor.extract_tables(pdf_path)
            
            # 提取文档结构
            result["structure"] = self._extract_structure(result["full_text"])
            
        except ImportError:
            # 回退到pypdf
            try:
                from pypdf import PdfReader
                
                reader = PdfReader(pdf_path)
                result["structure"].total_pages = len(reader.pages)
                
                all_text = []
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text() or ""
                    all_text.append(text)
                    
                    chunks = self.chunker.chunk(text, page_num)
                    result["chunks"].extend(chunks)
                
                result["full_text"] = "\n\n".join(all_text)
                result["structure"] = self._extract_structure(result["full_text"])
                
            except Exception as e:
                result["error"] = f"PDF处理失败: {e}"
        
        except Exception as e:
            result["error"] = f"PDF处理失败: {e}"
        
        return result
    
    def _extract_structure(self, text: str) -> PDFStructure:
        """提取文档结构"""
        structure = PDFStructure()
        
        # 提取标题（通常在前几行）
        lines = text.split('\n')[:20]
        for line in lines:
            line = line.strip()
            if len(line) > 5 and len(line) < 100:
                if '报告' in line or '研究' in line or '分析' in line:
                    structure.title = line
                    break
        
        # 提取日期
        date_patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{4}-\d{1,2}-\d{1,2})',
            r'(\d{4}/\d{1,2}/\d{1,2})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text[:2000])
            if match:
                structure.date = match.group(1)
                break
        
        # 提取章节目录
        sections = []
        for pattern in SemanticChunker.SECTION_PATTERNS:
            matches = re.findall(f'{pattern}.*', text, re.MULTILINE)
            for match in matches[:20]:  # 限制数量
                if len(match.strip()) < 100:
                    sections.append({"title": match.strip()})
        
        structure.sections = sections
        
        return structure
    
    def get_table_of_contents(self, pdf_path: str) -> List[str]:
        """
        获取PDF目录
        
        Args:
            pdf_path: PDF文件路径
        
        Returns:
            List[str]: 目录列表
        """
        result = self.process(pdf_path)
        
        if "error" in result:
            return [result["error"]]
        
        toc = []
        
        # 从结构中提取
        for section in result["structure"].sections:
            toc.append(section.get("title", ""))
        
        # 从chunks中补充
        for chunk in result["chunks"]:
            if chunk.chunk_type == "title" and chunk.content not in toc:
                toc.append(chunk.content)
        
        return toc[:30]  # 限制数量


# 全局实例
semantic_chunker = SemanticChunker()
table_extractor = TableExtractor()
pdf_processor = EnhancedPDFProcessor()
