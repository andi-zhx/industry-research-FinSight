# memory_system/memory_manager.py
"""
全维投研记忆系统 - 增强版
核心改进：
1. 智能学习机制：从历史研报中学习最佳实践
2. 经验积累：记录成功的研究模式和失败案例
3. 上下文感知：根据行业特征提供针对性建议
4. 知识图谱：构建行业关联知识网络
"""

import datetime
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

from ingestion.pdf_ingest import PDFIngestor
from memory_system.vector_store.chroma_client import ChromaVectorStore
from rag.retriever import VectorRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter


class IndustryKnowledgeGraph:
    """
    行业知识图谱
    记录行业间的关联关系、产业链结构、关键指标等
    """
    
    def __init__(self):
        self.industry_relations: Dict[str, Dict] = {}  # 行业关联关系
        self.supply_chain_templates: Dict[str, Dict] = {}  # 产业链模板
        self.key_metrics: Dict[str, List[str]] = {}  # 行业关键指标
        self._init_default_knowledge()
    
    def _init_default_knowledge(self):
        """初始化默认行业知识"""
        # 行业关联关系
        self.industry_relations = {
            "人工智能": {
                "upstream": ["半导体", "芯片设计", "数据服务", "云计算"],
                "downstream": ["智能制造", "智慧医疗", "自动驾驶", "金融科技"],
                "related": ["大数据", "物联网", "5G通信"]
            },
            "新能源汽车": {
                "upstream": ["锂电池", "电机", "电控系统", "稀土材料"],
                "downstream": ["出行服务", "充电桩", "汽车后市场"],
                "related": ["智能驾驶", "车联网", "储能"]
            },
            "半导体": {
                "upstream": ["硅片", "光刻机", "EDA工具", "特种气体"],
                "downstream": ["消费电子", "汽车电子", "工业控制"],
                "related": ["人工智能", "5G通信", "物联网"]
            },
            "生物医药": {
                "upstream": ["原料药", "医疗器械", "CRO/CDMO"],
                "downstream": ["医院", "药店", "医疗服务"],
                "related": ["基因检测", "精准医疗", "医疗AI"]
            }
        }
        
        # 产业链分析模板
        self.supply_chain_templates = {
            "default": {
                "upstream": ["原材料供应", "核心零部件", "设备供应商"],
                "midstream": ["核心制造", "技术研发", "系统集成"],
                "downstream": ["终端应用", "渠道分销", "售后服务"]
            },
            "人工智能": {
                "upstream": ["AI芯片", "算力基础设施", "数据服务", "开发框架"],
                "midstream": ["算法研发", "模型训练", "平台服务"],
                "downstream": ["行业应用", "消费级产品", "解决方案"]
            }
        }
        
        # 行业关键指标
        self.key_metrics = {
            "人工智能": [
                "核心产业规模", "企业数量", "专利申请量", "融资规模",
                "算力规模", "人才数量", "应用渗透率"
            ],
            "新能源汽车": [
                "产销量", "渗透率", "电池装机量", "充电桩数量",
                "出口量", "市场集中度"
            ],
            "半导体": [
                "产值规模", "设计企业数量", "制造产能", "国产化率",
                "研发投入", "专利数量"
            ]
        }
    
    def get_related_industries(self, industry: str) -> Dict[str, List[str]]:
        """获取相关行业"""
        return self.industry_relations.get(industry, {
            "upstream": [],
            "downstream": [],
            "related": []
        })
    
    def get_supply_chain_template(self, industry: str) -> Dict[str, List[str]]:
        """获取产业链模板"""
        return self.supply_chain_templates.get(
            industry, 
            self.supply_chain_templates["default"]
        )
    
    def get_key_metrics(self, industry: str) -> List[str]:
        """获取行业关键指标"""
        return self.key_metrics.get(industry, [
            "市场规模", "增长率", "竞争格局", "政策支持", "技术趋势"
        ])


class ResearchExperience:
    """
    研究经验管理器
    记录和学习成功的研究模式
    """
    
    def __init__(self):
        self.successful_patterns: List[Dict] = []  # 成功的研究模式
        self.failed_patterns: List[Dict] = []  # 失败案例
        self.best_practices: Dict[str, List[str]] = {}  # 最佳实践
        self.quality_scores: Dict[str, float] = {}  # 研报质量评分
        self._init_best_practices()
    
    def _init_best_practices(self):
        """初始化最佳实践"""
        self.best_practices = {
            "数据引用": [
                "所有数据必须标注来源和时间",
                "优先使用官方统计数据和权威机构报告",
                "对比多个数据源进行交叉验证",
                "注明数据的统计口径和定义"
            ],
            "产业链分析": [
                "明确上中下游的划分标准",
                "分析各环节的价值分配和议价能力",
                "识别产业链的关键卡脖子环节",
                "评估国产替代的进展和机会"
            ],
            "竞争格局": [
                "使用CR5/CR10等集中度指标",
                "分析龙头企业的核心竞争力",
                "关注新进入者和潜在颠覆者",
                "评估行业壁垒的高低"
            ],
            "投资建议": [
                "投资建议必须有明确的逻辑支撑",
                "区分短期机会和长期价值",
                "明确风险提示和应对策略",
                "给出具体的投资标的或方向"
            ]
        }
    
    def record_success(self, pattern: Dict):
        """记录成功的研究模式"""
        pattern["timestamp"] = datetime.datetime.now().isoformat()
        pattern["type"] = "success"
        self.successful_patterns.append(pattern)
        
        # 限制存储数量
        if len(self.successful_patterns) > 100:
            self.successful_patterns = self.successful_patterns[-100:]
    
    def record_failure(self, pattern: Dict, reason: str):
        """记录失败案例"""
        pattern["timestamp"] = datetime.datetime.now().isoformat()
        pattern["type"] = "failure"
        pattern["reason"] = reason
        self.failed_patterns.append(pattern)
        
        if len(self.failed_patterns) > 50:
            self.failed_patterns = self.failed_patterns[-50:]
    
    def get_recommendations(self, industry: str, dimension: str) -> List[str]:
        """获取针对特定维度的建议"""
        recommendations = self.best_practices.get(dimension, [])
        
        # 从成功模式中学习
        for pattern in self.successful_patterns[-10:]:
            if pattern.get("industry") == industry and pattern.get("dimension") == dimension:
                if pattern.get("key_insight"):
                    recommendations.append(f"[历史经验] {pattern['key_insight']}")
        
        return recommendations
    
    def update_quality_score(self, report_id: str, score: float):
        """更新研报质量评分"""
        self.quality_scores[report_id] = score


class MemoryManager:
    """
    全维投研记忆系统 - 增强版
    支持：PDF原文、Agent产出的事实、观点、结论、正文段落
    新增：智能学习、经验积累、知识图谱
    """

    def __init__(self, persist_dir: str):
        self.vector_store = ChromaVectorStore(persist_dir)
        self.retriever = VectorRetriever(self.vector_store)
        self.pdf_ingestor = PDFIngestor()
        
        # 文本切分器
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "；", " ", ""]
        )
        
        # 新增：知识图谱和经验管理
        self.knowledge_graph = IndustryKnowledgeGraph()
        self.experience = ResearchExperience()
        
        # 缓存
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 3600  # 缓存有效期（秒）
        
        # 统计信息
        self.stats = {
            "total_insights": 0,
            "total_recalls": 0,
            "industries_covered": set(),
            "last_update": None
        }

    # ------------------ 存入 (Write) ------------------

    def save_insight(self, content: str, category: str, metadata: dict):
        """
        核心方法：存储 Agent 的产出
        :param content: 文本内容
        :param category: 'fact' | 'opinion' | 'conclusion' | 'report_segment' | 'experience'
        :param metadata: {industry, year, province, focus, source_agent}
        """
        if not content:
            return

        # 自动补全元数据
        meta = metadata.copy()
        meta.update({
            "category": category,
            "ingest_time": datetime.datetime.now().isoformat(),
            "type": "agent_memory",
            "content_hash": hashlib.md5(content.encode()).hexdigest()[:8]
        })

        # 根据内容长度决定是否切分
        if len(content) < 500:
            chunks = [content]
        else:
            chunks = self.splitter.split_text(content)
            
        metadatas = [meta for _ in chunks]
        self.vector_store.add_texts(chunks, metadatas)
        
        # 更新统计
        self.stats["total_insights"] += len(chunks)
        if metadata.get("industry"):
            self.stats["industries_covered"].add(metadata["industry"])
        self.stats["last_update"] = datetime.datetime.now().isoformat()
        
        print(f"🧠 [Memory] 已存储 {len(chunks)} 条 {category} 记忆")

    def save_research_experience(self, industry: str, dimension: str, 
                                  insight: str, success: bool = True):
        """
        保存研究经验
        :param industry: 行业
        :param dimension: 研究维度
        :param insight: 关键洞察
        :param success: 是否成功
        """
        pattern = {
            "industry": industry,
            "dimension": dimension,
            "key_insight": insight
        }
        
        if success:
            self.experience.record_success(pattern)
        else:
            self.experience.record_failure(pattern, "质量不达标")
        
        # 同时存入向量库
        self.save_insight(
            content=f"[{industry}][{dimension}] {insight}",
            category="experience",
            metadata={
                "industry": industry,
                "dimension": dimension,
                "success": success
            }
        )

    def ingest_pdf(self, file_path: str, metadata: dict):
        """导入PDF文档"""
        raw_text = self.pdf_ingestor.ingest(file_path)
        chunks = self.splitter.split_text(raw_text)
        
        # 增强元数据
        enhanced_meta = metadata.copy()
        enhanced_meta["source_type"] = "pdf"
        enhanced_meta["file_path"] = file_path
        
        metadatas = [enhanced_meta for _ in chunks]
        self.vector_store.add_texts(chunks, metadatas)
        
        print(f"📄 [Memory] 已导入PDF: {file_path}, {len(chunks)} 个片段")

    # ------------------ 召回 (Read) ------------------

    def recall_memory(self, query: str, category: str = None, 
                      k: int = 5, industry: str = None) -> List[Dict]:
        """
        精准召回：支持按 category 和 industry 过滤
        """
        # 检查缓存
        cache_key = f"{query}_{category}_{k}_{industry}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if (datetime.datetime.now() - cached["time"]).seconds < self._cache_ttl:
                return cached["data"]
        
        # 召回更多结果以便过滤
        results = self.retriever.retrieve(query, k=k * 3)
        
        # 过滤
        filtered_results = []
        for doc in results:
            # 兼容不同的返回格式
            if hasattr(doc, 'metadata'):
                meta = doc.metadata
                content = doc.page_content
            elif isinstance(doc, dict):
                meta = doc.get('metadata', {})
                content = doc.get('content', doc.get('page_content', ''))
            else:
                continue
            
            # 按category过滤
            if category and meta.get('category') != category:
                continue
            
            # 按industry过滤
            if industry and meta.get('industry') != industry:
                continue
            
            filtered_results.append({
                "content": content,
                "metadata": meta
            })
            
            if len(filtered_results) >= k:
                break
        
        # 更新缓存
        self._cache[cache_key] = {
            "data": filtered_results,
            "time": datetime.datetime.now()
        }
        
        # 更新统计
        self.stats["total_recalls"] += 1
        
        return filtered_results

    def recall_similar_reports(self, industry: str, province: str = None, 
                                k: int = 3) -> List[Dict]:
        """
        召回相似的历史研报
        用于学习成功的研究模式
        """
        query = f"{province or ''} {industry} 行业研究报告"
        return self.recall_memory(
            query=query,
            category="report_segment",
            k=k,
            industry=industry
        )

    # ------------------ 智能建议 ------------------

    def get_research_suggestions(self, industry: str, 
                                  dimension: str = None) -> Dict[str, Any]:
        """
        获取研究建议
        基于知识图谱和历史经验
        """
        suggestions = {
            "related_industries": self.knowledge_graph.get_related_industries(industry),
            "supply_chain_template": self.knowledge_graph.get_supply_chain_template(industry),
            "key_metrics": self.knowledge_graph.get_key_metrics(industry),
            "best_practices": [],
            "historical_insights": []
        }
        
        # 获取最佳实践
        if dimension:
            suggestions["best_practices"] = self.experience.get_recommendations(
                industry, dimension
            )
        else:
            for dim in ["数据引用", "产业链分析", "竞争格局", "投资建议"]:
                suggestions["best_practices"].extend(
                    self.experience.get_recommendations(industry, dim)
                )
        
        # 召回历史洞察
        historical = self.recall_memory(
            query=f"{industry} 投资机会 风险",
            category="conclusion",
            k=5,
            industry=industry
        )
        suggestions["historical_insights"] = [
            h["content"] for h in historical
        ]
        
        return suggestions

    def get_industry_context(self, industry: str, province: str = None) -> str:
        """
        获取行业上下文信息
        用于增强Agent的背景知识
        """
        context_parts = []
        
        # 1. 相关行业
        relations = self.knowledge_graph.get_related_industries(industry)
        if relations.get("upstream"):
            context_parts.append(f"上游关联行业：{', '.join(relations['upstream'])}")
        if relations.get("downstream"):
            context_parts.append(f"下游关联行业：{', '.join(relations['downstream'])}")
        
        # 2. 关键指标
        metrics = self.knowledge_graph.get_key_metrics(industry)
        if metrics:
            context_parts.append(f"关键研究指标：{', '.join(metrics)}")
        
        # 3. 历史研究经验
        experiences = self.recall_memory(
            query=f"{industry} 研究经验",
            category="experience",
            k=3
        )
        if experiences:
            context_parts.append("历史研究经验：")
            for exp in experiences:
                context_parts.append(f"  - {exp['content'][:100]}...")
        
        return "\n".join(context_parts)

    # ------------------ 统计与维护 ------------------

    def get_stats(self) -> Dict[str, Any]:
        """获取记忆系统统计信息"""
        return {
            "total_insights": self.stats["total_insights"],
            "total_recalls": self.stats["total_recalls"],
            "industries_covered": list(self.stats["industries_covered"]),
            "last_update": self.stats["last_update"],
            "successful_patterns": len(self.experience.successful_patterns),
            "failed_patterns": len(self.experience.failed_patterns)
        }

    def clear_cache(self):
        """清理缓存"""
        self._cache.clear()
        print("🧹 [Memory] 缓存已清理")

    def export_knowledge(self, output_path: str):
        """导出知识库"""
        knowledge = {
            "industry_relations": self.knowledge_graph.industry_relations,
            "supply_chain_templates": self.knowledge_graph.supply_chain_templates,
            "key_metrics": self.knowledge_graph.key_metrics,
            "best_practices": self.experience.best_practices,
            "successful_patterns": self.experience.successful_patterns[-20:],
            "stats": self.get_stats()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, ensure_ascii=False, indent=2)
        
        print(f"📤 [Memory] 知识库已导出: {output_path}")

    def import_knowledge(self, input_path: str):
        """导入知识库"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                knowledge = json.load(f)
            
            # 合并行业关系
            self.knowledge_graph.industry_relations.update(
                knowledge.get("industry_relations", {})
            )
            
            # 合并产业链模板
            self.knowledge_graph.supply_chain_templates.update(
                knowledge.get("supply_chain_templates", {})
            )
            
            # 合并关键指标
            self.knowledge_graph.key_metrics.update(
                knowledge.get("key_metrics", {})
            )
            
            # 合并最佳实践
            for key, practices in knowledge.get("best_practices", {}).items():
                if key in self.experience.best_practices:
                    self.experience.best_practices[key].extend(practices)
                else:
                    self.experience.best_practices[key] = practices
            
            print(f"📥 [Memory] 知识库已导入: {input_path}")
            
        except Exception as e:
            print(f"⚠️ [Memory] 知识库导入失败: {e}")


# 全局单例
memory_manager = MemoryManager(persist_dir="./knowledge_base/vector_store")
