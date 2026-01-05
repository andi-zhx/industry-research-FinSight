# agent_system/quality/data_quality.py
"""
数据质量评估模块
实现数据覆盖率检查、路由决策、质量评分

核心功能：
1. 数据覆盖率检查 - 评估研究数据是否完整
2. 路由决策 - 决定是否需要回退重新搜索
3. 质量评分 - 对研究产出进行量化评估
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class DataDimension(Enum):
    """研究数据维度"""
    FINANCIAL = "financial"  # 财务数据
    POLICY = "policy"  # 政策数据
    MARKET_SIZE = "market_size"  # 市场规模
    SUPPLY_CHAIN = "supply_chain"  # 产业链
    COMPETITIVE = "competitive"  # 竞争格局
    BUSINESS_MODEL = "business_model"  # 商业模式


@dataclass
class DataRequirement:
    """数据需求定义"""
    dimension: DataDimension
    required_fields: List[str]
    weight: float = 1.0  # 权重
    min_sources: int = 2  # 最少数据来源数
    

@dataclass
class QualityScore:
    """质量评分结果"""
    total_score: float
    dimension_scores: Dict[str, float]
    missing_data: List[str]
    weak_areas: List[str]
    recommendations: List[str]
    pass_threshold: bool


class DataQualityChecker:
    """
    数据质量检查器
    评估研究数据的完整性和质量
    """
    
    # 默认数据需求配置
    DEFAULT_REQUIREMENTS = {
        DataDimension.FINANCIAL: DataRequirement(
            dimension=DataDimension.FINANCIAL,
            required_fields=[
                "营收", "净利润", "毛利率", "市值", "PE", "PB",
                "增长率", "ROE", "资产负债率"
            ],
            weight=1.5,
            min_sources=2
        ),
        DataDimension.POLICY: DataRequirement(
            dimension=DataDimension.POLICY,
            required_fields=[
                "国家政策", "地方政策", "补贴", "规划", "监管"
            ],
            weight=1.0,
            min_sources=2
        ),
        DataDimension.MARKET_SIZE: DataRequirement(
            dimension=DataDimension.MARKET_SIZE,
            required_fields=[
                "市场规模", "增速", "CAGR", "渗透率", "预测"
            ],
            weight=1.5,
            min_sources=2
        ),
        DataDimension.SUPPLY_CHAIN: DataRequirement(
            dimension=DataDimension.SUPPLY_CHAIN,
            required_fields=[
                "上游", "中游", "下游", "产业链", "供应商", "客户"
            ],
            weight=1.2,
            min_sources=2
        ),
        DataDimension.COMPETITIVE: DataRequirement(
            dimension=DataDimension.COMPETITIVE,
            required_fields=[
                "龙头企业", "市场份额", "CR5", "竞争格局", "壁垒"
            ],
            weight=1.0,
            min_sources=2
        ),
        DataDimension.BUSINESS_MODEL: DataRequirement(
            dimension=DataDimension.BUSINESS_MODEL,
            required_fields=[
                "收入结构", "成本结构", "盈利模式", "客户", "定价"
            ],
            weight=0.8,
            min_sources=1
        )
    }
    
    def __init__(self, pass_threshold: float = 0.8):
        """
        初始化质量检查器
        
        Args:
            pass_threshold: 通过阈值，默认80%
        """
        self.pass_threshold = pass_threshold
        self.requirements = self.DEFAULT_REQUIREMENTS.copy()
    
    def check_coverage(self, research_content: str, 
                       dimensions: List[DataDimension] = None) -> QualityScore:
        """
        检查数据覆盖率
        
        Args:
            research_content: 研究内容文本
            dimensions: 要检查的维度列表，默认检查所有维度
        
        Returns:
            QualityScore: 质量评分结果
        """
        if dimensions is None:
            dimensions = list(DataDimension)
        
        dimension_scores = {}
        missing_data = []
        weak_areas = []
        total_weight = 0
        weighted_score = 0
        
        for dim in dimensions:
            req = self.requirements.get(dim)
            if not req:
                continue
            
            # 计算该维度的覆盖率
            found_fields = []
            for field in req.required_fields:
                if self._field_exists(research_content, field):
                    found_fields.append(field)
            
            coverage = len(found_fields) / len(req.required_fields) if req.required_fields else 0
            dimension_scores[dim.value] = coverage
            
            # 记录缺失数据
            missing = set(req.required_fields) - set(found_fields)
            if missing:
                missing_data.extend([f"[{dim.value}] {f}" for f in missing])
            
            # 标记薄弱环节
            if coverage < 0.6:
                weak_areas.append(f"{dim.value}: 覆盖率仅{coverage*100:.0f}%")
            
            # 加权计算
            weighted_score += coverage * req.weight
            total_weight += req.weight
        
        # 计算总分
        total_score = weighted_score / total_weight if total_weight > 0 else 0
        
        # 生成建议
        recommendations = self._generate_recommendations(
            dimension_scores, missing_data, weak_areas
        )
        
        return QualityScore(
            total_score=total_score,
            dimension_scores=dimension_scores,
            missing_data=missing_data,
            weak_areas=weak_areas,
            recommendations=recommendations,
            pass_threshold=total_score >= self.pass_threshold
        )
    
    def _field_exists(self, content: str, field: str) -> bool:
        """检查字段是否存在于内容中"""
        # 支持多种匹配模式
        patterns = [
            field,  # 精确匹配
            field.replace("率", ""),  # 去掉"率"
            field + "：",  # 带冒号
            field + ":",
        ]
        
        for pattern in patterns:
            if pattern in content:
                return True
        
        # 检查是否有相关数字
        number_pattern = rf"{field}[：:]\s*[\d,\.]+[亿万%]?"
        if re.search(number_pattern, content):
            return True
        
        return False
    
    def _generate_recommendations(self, scores: Dict[str, float],
                                   missing: List[str], 
                                   weak: List[str]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 针对薄弱环节的建议
        for area in weak:
            dim = area.split(":")[0]
            if dim == "financial":
                recommendations.append(
                    "建议补充龙头企业的详细财务数据，包括近3年营收、净利润、毛利率等"
                )
            elif dim == "market_size":
                recommendations.append(
                    "建议补充权威机构的市场规模预测数据，如IDC、Gartner、艾瑞等"
                )
            elif dim == "supply_chain":
                recommendations.append(
                    "建议完善产业链各环节分析，明确上中下游的关键企业和价值分配"
                )
            elif dim == "policy":
                recommendations.append(
                    "建议补充最新的国家和地方产业政策，特别是补贴和扶持措施"
                )
        
        # 通用建议
        if len(missing) > 5:
            recommendations.append(
                f"数据缺失较多（{len(missing)}项），建议扩大搜索范围或更换关键词"
            )
        
        return recommendations


class ResearchRouter:
    """
    研究路由器
    根据数据质量决定下一步动作
    """
    
    class Action(Enum):
        PROCEED = "proceed"  # 继续下一阶段
        RETRY_SEARCH = "retry_search"  # 重新搜索
        EXPAND_KEYWORDS = "expand_keywords"  # 扩展关键词
        HUMAN_REVIEW = "human_review"  # 人工介入
    
    def __init__(self, quality_checker: DataQualityChecker = None):
        self.quality_checker = quality_checker or DataQualityChecker()
        self.retry_count = 0
        self.max_retries = 2
    
    def decide(self, research_content: str, 
               context: Dict[str, Any] = None) -> Tuple[Action, Dict]:
        """
        决定下一步动作
        
        Args:
            research_content: 研究内容
            context: 上下文信息
        
        Returns:
            Tuple[Action, Dict]: (动作, 附加信息)
        """
        context = context or {}
        
        # 检查数据质量
        quality = self.quality_checker.check_coverage(research_content)
        
        result_info = {
            "quality_score": quality.total_score,
            "dimension_scores": quality.dimension_scores,
            "missing_data": quality.missing_data,
            "recommendations": quality.recommendations
        }
        
        # 决策逻辑
        if quality.pass_threshold:
            # 质量达标，继续
            return self.Action.PROCEED, result_info
        
        if self.retry_count >= self.max_retries:
            # 重试次数用尽，人工介入
            result_info["reason"] = f"已重试{self.retry_count}次，建议人工介入"
            return self.Action.HUMAN_REVIEW, result_info
        
        # 根据薄弱环节决定动作
        if quality.total_score < 0.5:
            # 严重不足，重新搜索
            self.retry_count += 1
            result_info["retry_count"] = self.retry_count
            result_info["suggested_keywords"] = self._suggest_keywords(quality)
            return self.Action.RETRY_SEARCH, result_info
        else:
            # 部分不足，扩展关键词
            self.retry_count += 1
            result_info["retry_count"] = self.retry_count
            result_info["expand_dimensions"] = quality.weak_areas
            return self.Action.EXPAND_KEYWORDS, result_info
    
    def _suggest_keywords(self, quality: QualityScore) -> List[str]:
        """根据缺失数据建议搜索关键词"""
        keywords = []
        
        for missing in quality.missing_data[:5]:  # 取前5个
            # 提取字段名
            field = missing.split("] ")[-1] if "] " in missing else missing
            keywords.append(field)
        
        return keywords
    
    def reset(self):
        """重置重试计数"""
        self.retry_count = 0


class DataRequirementGenerator:
    """
    数据需求清单生成器
    根据研究主题生成具体的数据需求
    """
    
    def generate(self, industry: str, province: str, 
                 target_year: str, focus: str) -> Dict[str, List[str]]:
        """
        生成数据需求清单
        
        Args:
            industry: 行业
            province: 省份
            target_year: 目标年份
            focus: 研究侧重点
        
        Returns:
            Dict: 数据需求清单
        """
        requirements = {
            "必需数据": [
                f"{industry}行业{target_year}年市场规模及预测",
                f"{industry}行业近5年CAGR（复合增长率）",
                f"{province}{industry}行业企业数量及分布",
                f"{industry}产业链上中下游结构图",
                f"{industry}行业CR5/CR10市场集中度",
                f"{industry}行业龙头企业财务数据（营收、净利润、毛利率）",
            ],
            "政策数据": [
                f"国家{industry}产业政策（十四五规划）",
                f"{province}{industry}产业扶持政策",
                f"{industry}行业补贴政策及金额",
                f"{industry}行业监管政策及合规要求",
            ],
            "产业链数据": [
                f"{industry}上游原材料/零部件供应商名单",
                f"{industry}中游核心制造企业名单",
                f"{industry}下游应用场景及客户类型",
                f"{industry}产业链各环节利润分配比例",
                f"{industry}产业链关键卡脖子环节",
            ],
            "竞争格局数据": [
                f"{industry}行业TOP10企业名单及市场份额",
                f"{industry}行业新进入者及潜在竞争者",
                f"{industry}行业进入壁垒分析",
                f"{province}{industry}行业重点企业名单",
            ],
            "投资相关数据": [
                f"{industry}行业近3年融资事件及金额",
                f"{industry}行业估值水平（PE/PS倍数）",
                f"{industry}行业投资热点及趋势",
            ]
        }
        
        # 根据focus添加额外需求
        if "投资" in focus or "VC" in focus or "PE" in focus:
            requirements["投资相关数据"].extend([
                f"{industry}行业退出案例（IPO/并购）",
                f"{industry}行业投资回报率参考",
            ])
        
        if "产业链" in focus:
            requirements["产业链数据"].extend([
                f"{industry}产业链国产化率",
                f"{industry}产业链进口替代进展",
            ])
        
        return requirements


# 全局实例
data_quality_checker = DataQualityChecker()
research_router = ResearchRouter(data_quality_checker)
requirement_generator = DataRequirementGenerator()
