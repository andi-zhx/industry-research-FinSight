# agent_system/rag/agentic_rag.py
"""
Agentic RAG 模块
从Naive RAG升级到智能RAG

核心功能：
1. Query Rewriting - 查询改写，将用户问题分解为多个子查询
2. Reranking - 重排序，使用交叉编码器对检索结果重新排序
3. Self-Reflective RAG - 自省式RAG，检索后判断是否需要补充检索
4. Hybrid Search - 混合检索，结合向量检索和关键词检索
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


@dataclass
class RetrievedChunk:
    """检索到的文档片段"""
    content: str
    source: str
    score: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RAGResult:
    """RAG检索结果"""
    query: str
    sub_queries: List[str]
    chunks: List[RetrievedChunk]
    answer: str = ""
    confidence: float = 0.0
    need_more_info: bool = False
    missing_aspects: List[str] = None
    
    def __post_init__(self):
        if self.missing_aspects is None:
            self.missing_aspects = []


class QueryRewriter:
    """
    查询改写器
    将复杂问题分解为多个子查询
    """
    
    # 行业研究常见查询模式
    QUERY_PATTERNS = {
        "市场规模": [
            "{industry}市场规模 {year}",
            "{industry}行业规模 增速 CAGR",
            "{industry}市场预测 趋势"
        ],
        "产业链": [
            "{industry}产业链 上游 原材料",
            "{industry}产业链 中游 制造",
            "{industry}产业链 下游 应用",
            "{industry}产业链图谱 全景"
        ],
        "竞争格局": [
            "{industry}龙头企业 市场份额",
            "{industry}CR5 CR10 集中度",
            "{industry}竞争格局 壁垒"
        ],
        "政策": [
            "{industry}产业政策 国家",
            "{province}{industry}政策 补贴",
            "{industry}十四五 规划"
        ],
        "财务": [
            "{company}营收 净利润 {year}",
            "{company}毛利率 ROE",
            "{company}财务数据 年报"
        ]
    }
    
    def __init__(self):
        self.context = {}
    
    def set_context(self, industry: str = "", province: str = "", 
                    year: str = "", company: str = ""):
        """设置查询上下文"""
        self.context = {
            "industry": industry,
            "province": province,
            "year": year,
            "company": company
        }
    
    def rewrite(self, query: str) -> List[str]:
        """
        改写查询
        
        Args:
            query: 原始查询
        
        Returns:
            List[str]: 改写后的子查询列表
        """
        sub_queries = [query]  # 保留原始查询
        
        # 识别查询意图
        intent = self._detect_intent(query)
        
        # 根据意图生成子查询
        if intent in self.QUERY_PATTERNS:
            patterns = self.QUERY_PATTERNS[intent]
            for pattern in patterns:
                sub_query = pattern.format(**self.context)
                if sub_query.strip() and sub_query not in sub_queries:
                    sub_queries.append(sub_query)
        
        # 添加同义词扩展
        expanded = self._expand_synonyms(query)
        sub_queries.extend([q for q in expanded if q not in sub_queries])
        
        # 限制子查询数量
        return sub_queries[:5]
    
    def _detect_intent(self, query: str) -> str:
        """检测查询意图"""
        intent_keywords = {
            "市场规模": ["规模", "市场", "增速", "CAGR", "预测"],
            "产业链": ["产业链", "上游", "中游", "下游", "供应商"],
            "竞争格局": ["竞争", "龙头", "份额", "CR5", "集中度"],
            "政策": ["政策", "补贴", "规划", "监管", "扶持"],
            "财务": ["营收", "利润", "毛利", "ROE", "财务"]
        }
        
        query_lower = query.lower()
        for intent, keywords in intent_keywords.items():
            if any(kw in query_lower for kw in keywords):
                return intent
        
        return "general"
    
    def _expand_synonyms(self, query: str) -> List[str]:
        """同义词扩展"""
        synonyms = {
            "市场规模": ["行业规模", "市场空间", "市场容量"],
            "增速": ["增长率", "同比增长", "年增长"],
            "龙头企业": ["头部企业", "领先企业", "TOP企业"],
            "产业链": ["价值链", "供应链"],
            "竞争格局": ["市场格局", "竞争态势"],
        }
        
        expanded = []
        for term, syns in synonyms.items():
            if term in query:
                for syn in syns:
                    expanded.append(query.replace(term, syn))
        
        return expanded


class ChunkReranker:
    """
    文档片段重排序器
    使用多种策略对检索结果进行重排序
    """
    
    def __init__(self):
        # 关键词权重
        self.keyword_weights = {
            "数据": 1.5,
            "统计": 1.5,
            "报告": 1.3,
            "研究": 1.2,
            "分析": 1.2,
            "预测": 1.3,
            "官方": 1.5,
            "权威": 1.4,
            "年": 1.2,
            "亿": 1.3,
            "万": 1.2,
            "%": 1.3,
        }
        
        # 来源权重
        self.source_weights = {
            "国家统计局": 2.0,
            "工信部": 1.8,
            "发改委": 1.8,
            "IDC": 1.7,
            "Gartner": 1.7,
            "艾瑞": 1.6,
            "赛迪": 1.6,
            "年报": 1.5,
            "招股书": 1.5,
        }
    
    def rerank(self, chunks: List[RetrievedChunk], 
               query: str, top_k: int = 5) -> List[RetrievedChunk]:
        """
        重排序检索结果
        
        Args:
            chunks: 检索到的文档片段
            query: 原始查询
            top_k: 返回数量
        
        Returns:
            List[RetrievedChunk]: 重排序后的结果
        """
        if not chunks:
            return []
        
        # 计算综合得分
        scored_chunks = []
        for chunk in chunks:
            score = self._calculate_score(chunk, query)
            scored_chunks.append((chunk, score))
        
        # 按得分排序
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # 返回top_k
        return [c[0] for c in scored_chunks[:top_k]]
    
    def _calculate_score(self, chunk: RetrievedChunk, query: str) -> float:
        """计算综合得分"""
        score = chunk.score  # 基础分数（向量相似度）
        
        # 1. 关键词加权
        for keyword, weight in self.keyword_weights.items():
            if keyword in chunk.content:
                score *= weight
        
        # 2. 来源加权
        source = chunk.source.lower()
        for src, weight in self.source_weights.items():
            if src.lower() in source:
                score *= weight
                break
        
        # 3. 查询词匹配度
        query_terms = set(query.replace("，", " ").replace(",", " ").split())
        content_terms = set(chunk.content)
        overlap = len(query_terms & content_terms)
        score *= (1 + overlap * 0.1)
        
        # 4. 数据密度（包含数字的比例）
        numbers = re.findall(r'\d+\.?\d*', chunk.content)
        data_density = len(numbers) / max(len(chunk.content.split()), 1)
        score *= (1 + data_density * 0.5)
        
        # 5. 时效性（如果包含近年份）
        current_year = 2025
        for year in range(current_year - 2, current_year + 2):
            if str(year) in chunk.content:
                score *= 1.2
                break
        
        return score


class SelfReflectiveRAG:
    """
    自省式RAG
    检索后自动判断是否需要补充检索
    """
    
    # 数据完整性检查项
    COMPLETENESS_CHECKS = {
        "市场规模": ["规模", "亿", "万"],
        "增长率": ["增速", "增长", "%", "CAGR"],
        "企业数据": ["企业", "公司", "营收", "利润"],
        "产业链": ["上游", "中游", "下游"],
        "政策": ["政策", "规划", "补贴"],
    }
    
    def __init__(self, rewriter: QueryRewriter = None, 
                 reranker: ChunkReranker = None):
        self.rewriter = rewriter or QueryRewriter()
        self.reranker = reranker or ChunkReranker()
    
    def reflect(self, query: str, chunks: List[RetrievedChunk]) -> Dict[str, Any]:
        """
        自省检索结果
        
        Args:
            query: 原始查询
            chunks: 检索到的文档片段
        
        Returns:
            Dict: 自省结果
        """
        # 合并所有内容
        combined_content = "\n".join([c.content for c in chunks])
        
        # 检查数据完整性
        missing_aspects = []
        coverage = {}
        
        for aspect, keywords in self.COMPLETENESS_CHECKS.items():
            found = any(kw in combined_content for kw in keywords)
            coverage[aspect] = found
            if not found:
                missing_aspects.append(aspect)
        
        # 计算覆盖率
        coverage_rate = sum(coverage.values()) / len(coverage) if coverage else 0
        
        # 判断是否需要补充检索
        need_more = coverage_rate < 0.6 or len(missing_aspects) >= 2
        
        # 生成补充查询建议
        supplement_queries = []
        if need_more:
            for aspect in missing_aspects:
                supplement_queries.append(f"{self.rewriter.context.get('industry', '')} {aspect}")
        
        return {
            "coverage": coverage,
            "coverage_rate": coverage_rate,
            "missing_aspects": missing_aspects,
            "need_more_retrieval": need_more,
            "supplement_queries": supplement_queries,
            "confidence": coverage_rate
        }
    
    def retrieve_with_reflection(self, query: str, 
                                  retriever_func, 
                                  max_iterations: int = 2) -> RAGResult:
        """
        带自省的检索流程
        
        Args:
            query: 原始查询
            retriever_func: 检索函数
            max_iterations: 最大迭代次数
        
        Returns:
            RAGResult: 检索结果
        """
        # 1. 查询改写
        sub_queries = self.rewriter.rewrite(query)
        
        all_chunks = []
        
        for iteration in range(max_iterations):
            # 2. 执行检索
            for sub_query in sub_queries:
                chunks = retriever_func(sub_query)
                all_chunks.extend(chunks)
            
            # 3. 去重
            seen = set()
            unique_chunks = []
            for chunk in all_chunks:
                content_hash = hash(chunk.content[:100])
                if content_hash not in seen:
                    seen.add(content_hash)
                    unique_chunks.append(chunk)
            
            # 4. 重排序
            ranked_chunks = self.reranker.rerank(unique_chunks, query, top_k=10)
            
            # 5. 自省
            reflection = self.reflect(query, ranked_chunks)
            
            if not reflection["need_more_retrieval"]:
                # 数据足够，返回结果
                return RAGResult(
                    query=query,
                    sub_queries=sub_queries,
                    chunks=ranked_chunks,
                    confidence=reflection["confidence"],
                    need_more_info=False
                )
            
            # 6. 补充查询
            sub_queries = reflection["supplement_queries"]
            if not sub_queries:
                break
        
        # 返回最终结果（可能不完整）
        return RAGResult(
            query=query,
            sub_queries=sub_queries,
            chunks=ranked_chunks if 'ranked_chunks' in dir() else [],
            confidence=reflection.get("confidence", 0.5),
            need_more_info=True,
            missing_aspects=reflection.get("missing_aspects", [])
        )


class HybridSearcher:
    """
    混合检索器
    结合向量检索和关键词检索
    """
    
    def __init__(self, vector_weight: float = 0.7, keyword_weight: float = 0.3):
        """
        初始化混合检索器
        
        Args:
            vector_weight: 向量检索权重
            keyword_weight: 关键词检索权重
        """
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
    
    def search(self, query: str, 
               vector_results: List[RetrievedChunk],
               keyword_results: List[RetrievedChunk],
               top_k: int = 5) -> List[RetrievedChunk]:
        """
        混合检索
        
        Args:
            query: 查询
            vector_results: 向量检索结果
            keyword_results: 关键词检索结果
            top_k: 返回数量
        
        Returns:
            List[RetrievedChunk]: 混合结果
        """
        # 建立内容到分数的映射
        scores = {}
        
        # 向量检索分数
        for i, chunk in enumerate(vector_results):
            content_key = chunk.content[:100]
            rank_score = 1 / (i + 1)  # 倒数排名分数
            scores[content_key] = {
                "chunk": chunk,
                "vector_score": rank_score * self.vector_weight,
                "keyword_score": 0
            }
        
        # 关键词检索分数
        for i, chunk in enumerate(keyword_results):
            content_key = chunk.content[:100]
            rank_score = 1 / (i + 1)
            
            if content_key in scores:
                scores[content_key]["keyword_score"] = rank_score * self.keyword_weight
            else:
                scores[content_key] = {
                    "chunk": chunk,
                    "vector_score": 0,
                    "keyword_score": rank_score * self.keyword_weight
                }
        
        # 计算综合分数并排序
        results = []
        for content_key, data in scores.items():
            total_score = data["vector_score"] + data["keyword_score"]
            chunk = data["chunk"]
            chunk.score = total_score
            results.append((chunk, total_score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        
        return [r[0] for r in results[:top_k]]


# 全局实例
query_rewriter = QueryRewriter()
chunk_reranker = ChunkReranker()
self_reflective_rag = SelfReflectiveRAG(query_rewriter, chunk_reranker)
hybrid_searcher = HybridSearcher()
