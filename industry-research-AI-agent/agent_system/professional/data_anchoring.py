# agent_system/professional/data_anchoring.py
"""
锚定型数据框架模块
解决差距一：数据可信度层级不够

核心理念：
- 从"推导型"数据升级为"锚定型"数据
- 每个关键数字必须有明确的锚点来源
- 测算逻辑必须可拆解、可验证
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class DataSourceTier(Enum):
    """数据来源层级"""
    TIER_1 = "一级来源"  # 官方统计、上市公司公告
    TIER_2 = "二级来源"  # 权威研究机构、行业协会
    TIER_3 = "三级来源"  # 媒体报道、专家访谈
    TIER_4 = "四级来源"  # 推算、估计


@dataclass
class DataAnchor:
    """数据锚点"""
    value: str                    # 数值
    unit: str                     # 单位
    source: str                   # 来源
    source_tier: DataSourceTier   # 来源层级
    date: str                     # 数据日期
    methodology: str = ""         # 测算方法（如有）
    confidence: float = 1.0       # 置信度 0-1
    raw_reference: str = ""       # 原始引用文本
    
    def to_citation(self) -> str:
        """生成引用格式"""
        return f"{self.value}{self.unit}（来源：{self.source}，{self.date}）"
    
    def to_detailed_citation(self) -> str:
        """生成详细引用格式"""
        tier_label = self.source_tier.value
        result = f"{self.value}{self.unit}\n"
        result += f"  - 来源：{self.source}（{tier_label}）\n"
        result += f"  - 日期：{self.date}\n"
        if self.methodology:
            result += f"  - 测算方法：{self.methodology}\n"
        result += f"  - 置信度：{self.confidence:.0%}"
        return result


@dataclass
class AnchoredDataPoint:
    """锚定型数据点"""
    metric_name: str              # 指标名称
    primary_anchor: DataAnchor    # 主锚点
    supporting_anchors: List[DataAnchor] = field(default_factory=list)  # 支撑锚点
    calculation_breakdown: str = ""  # 计算拆解
    cross_validation: str = ""    # 交叉验证说明
    
    def get_confidence_score(self) -> float:
        """计算综合置信度"""
        base_score = self.primary_anchor.confidence
        
        # 来源层级加权
        tier_weights = {
            DataSourceTier.TIER_1: 1.0,
            DataSourceTier.TIER_2: 0.85,
            DataSourceTier.TIER_3: 0.7,
            DataSourceTier.TIER_4: 0.5
        }
        tier_factor = tier_weights.get(self.primary_anchor.source_tier, 0.5)
        
        # 支撑锚点加分
        support_bonus = min(len(self.supporting_anchors) * 0.05, 0.15)
        
        # 交叉验证加分
        validation_bonus = 0.1 if self.cross_validation else 0
        
        return min(base_score * tier_factor + support_bonus + validation_bonus, 1.0)
    
    def to_professional_format(self) -> str:
        """生成专业机构格式的数据引用"""
        result = f"**{self.metric_name}**：{self.primary_anchor.value}{self.primary_anchor.unit}\n\n"
        
        if self.calculation_breakdown:
            result += f"**测算拆解**：\n{self.calculation_breakdown}\n\n"
        
        result += f"**数据来源**：\n"
        result += f"- 主要来源：{self.primary_anchor.source}（{self.primary_anchor.source_tier.value}，{self.primary_anchor.date}）\n"
        
        for anchor in self.supporting_anchors:
            result += f"- 支撑来源：{anchor.source}（{anchor.source_tier.value}）\n"
        
        if self.cross_validation:
            result += f"\n**交叉验证**：{self.cross_validation}\n"
        
        result += f"\n**置信度评级**：{self.get_confidence_score():.0%}"
        
        return result


class DataAnchoringFramework:
    """
    锚定型数据框架
    
    核心功能：
    1. 数据来源分层管理
    2. 测算逻辑拆解
    3. 交叉验证
    4. 专业格式输出
    """
    
    # 一级来源（官方统计、上市公司公告）
    TIER_1_SOURCES = [
        "国家统计局", "央行", "银保监会", "证监会", "工信部",
        "发改委", "财政部", "商务部", "科技部",
        "省统计局", "市统计局",
        "上市公司年报", "上市公司招股书", "上市公司公告",
        "Wind", "Bloomberg", "同花顺iFinD"
    ]
    
    # 二级来源（权威研究机构、行业协会）
    TIER_2_SOURCES = [
        "IDC", "Gartner", "麦肯锡", "波士顿咨询", "贝恩",
        "艾瑞咨询", "易观", "中国信通院", "赛迪研究院",
        "中国人工智能产业发展联盟", "中国互联网协会",
        "行业协会", "产业联盟"
    ]
    
    # 三级来源（媒体报道、专家访谈）
    TIER_3_SOURCES = [
        "36氪", "虎嗅", "钛媒体", "界面新闻",
        "专家访谈", "行业会议", "企业高管发言"
    ]
    
    def __init__(self):
        self.data_points: Dict[str, AnchoredDataPoint] = {}
        self.validation_rules: List[callable] = []
    
    def classify_source(self, source: str) -> DataSourceTier:
        """自动分类数据来源层级"""
        source_lower = source.lower()
        
        for t1 in self.TIER_1_SOURCES:
            if t1.lower() in source_lower or source_lower in t1.lower():
                return DataSourceTier.TIER_1
        
        for t2 in self.TIER_2_SOURCES:
            if t2.lower() in source_lower or source_lower in t2.lower():
                return DataSourceTier.TIER_2
        
        for t3 in self.TIER_3_SOURCES:
            if t3.lower() in source_lower or source_lower in t3.lower():
                return DataSourceTier.TIER_3
        
        return DataSourceTier.TIER_4
    
    def create_anchored_data(
        self,
        metric_name: str,
        value: str,
        unit: str,
        source: str,
        date: str,
        methodology: str = "",
        supporting_sources: List[Dict] = None,
        calculation_breakdown: str = "",
        cross_validation: str = ""
    ) -> AnchoredDataPoint:
        """
        创建锚定型数据点
        
        Args:
            metric_name: 指标名称
            value: 数值
            unit: 单位
            source: 主要来源
            date: 数据日期
            methodology: 测算方法
            supporting_sources: 支撑来源列表
            calculation_breakdown: 计算拆解
            cross_validation: 交叉验证说明
        
        Returns:
            AnchoredDataPoint: 锚定型数据点
        """
        # 创建主锚点
        primary_anchor = DataAnchor(
            value=value,
            unit=unit,
            source=source,
            source_tier=self.classify_source(source),
            date=date,
            methodology=methodology
        )
        
        # 创建支撑锚点
        supporting_anchors = []
        if supporting_sources:
            for ss in supporting_sources:
                anchor = DataAnchor(
                    value=ss.get("value", value),
                    unit=ss.get("unit", unit),
                    source=ss.get("source", ""),
                    source_tier=self.classify_source(ss.get("source", "")),
                    date=ss.get("date", date)
                )
                supporting_anchors.append(anchor)
        
        # 创建数据点
        data_point = AnchoredDataPoint(
            metric_name=metric_name,
            primary_anchor=primary_anchor,
            supporting_anchors=supporting_anchors,
            calculation_breakdown=calculation_breakdown,
            cross_validation=cross_validation
        )
        
        # 存储
        self.data_points[metric_name] = data_point
        
        return data_point
    
    def generate_market_size_breakdown(
        self,
        total_value: float,
        segments: Dict[str, Dict],
        unit: str = "亿元"
    ) -> str:
        """
        生成市场规模拆解
        
        Args:
            total_value: 总规模
            segments: 细分市场 {名称: {value: 数值, source: 来源, logic: 推导逻辑}}
            unit: 单位
        
        Returns:
            str: 专业格式的市场规模拆解
        """
        result = f"**市场规模拆解**：{total_value}{unit}\n\n"
        result += "| 细分市场 | 规模 | 来源/推导逻辑 |\n"
        result += "|----------|------|---------------|\n"
        
        calculated_total = 0
        for name, data in segments.items():
            value = data.get("value", 0)
            source = data.get("source", "")
            logic = data.get("logic", "")
            
            source_text = source if source else logic
            result += f"| {name} | {value}{unit} | {source_text} |\n"
            calculated_total += value
        
        # 验证总和
        diff = abs(total_value - calculated_total)
        if diff > 0.1:
            result += f"\n⚠️ 注：细分市场合计 {calculated_total}{unit}，与总规模差异 {diff}{unit}\n"
        else:
            result += f"\n✅ 验证：细分市场合计 = {calculated_total}{unit}，与总规模一致\n"
        
        return result
    
    def generate_growth_rate_derivation(
        self,
        metric_name: str,
        historical_data: List[Tuple[str, float]],
        forecast_data: List[Tuple[str, float]],
        methodology: str
    ) -> str:
        """
        生成增长率推导
        
        Args:
            metric_name: 指标名称
            historical_data: 历史数据 [(年份, 数值), ...]
            forecast_data: 预测数据 [(年份, 数值), ...]
            methodology: 预测方法
        
        Returns:
            str: 专业格式的增长率推导
        """
        result = f"**{metric_name}增长率推导**\n\n"
        
        # 历史数据
        result += "**历史数据**：\n"
        result += "| 年份 | 数值 | 同比增速 |\n"
        result += "|------|------|----------|\n"
        
        prev_value = None
        for year, value in historical_data:
            if prev_value:
                growth = (value - prev_value) / prev_value * 100
                result += f"| {year} | {value} | {growth:+.1f}% |\n"
            else:
                result += f"| {year} | {value} | - |\n"
            prev_value = value
        
        # 计算历史CAGR
        if len(historical_data) >= 2:
            start_year, start_value = historical_data[0]
            end_year, end_value = historical_data[-1]
            years = int(end_year) - int(start_year)
            if years > 0 and start_value > 0:
                cagr = (pow(end_value / start_value, 1 / years) - 1) * 100
                result += f"\n**历史CAGR**（{start_year}-{end_year}）：{cagr:.1f}%\n"
        
        # 预测数据
        if forecast_data:
            result += "\n**预测数据**：\n"
            result += "| 年份 | 预测值 | 预测增速 |\n"
            result += "|------|--------|----------|\n"
            
            prev_value = historical_data[-1][1] if historical_data else None
            for year, value in forecast_data:
                if prev_value:
                    growth = (value - prev_value) / prev_value * 100
                    result += f"| {year}E | {value} | {growth:+.1f}% |\n"
                else:
                    result += f"| {year}E | {value} | - |\n"
                prev_value = value
        
        # 预测方法
        result += f"\n**预测方法**：{methodology}\n"
        
        return result
    
    def validate_data_consistency(self) -> List[str]:
        """验证数据一致性"""
        issues = []
        
        # 检查同一指标的不同来源是否一致
        for name, dp in self.data_points.items():
            if dp.supporting_anchors:
                primary_value = self._parse_number(dp.primary_anchor.value)
                for anchor in dp.supporting_anchors:
                    support_value = self._parse_number(anchor.value)
                    if primary_value and support_value:
                        diff_pct = abs(primary_value - support_value) / primary_value * 100
                        if diff_pct > 20:
                            issues.append(
                                f"⚠️ {name}：主来源({dp.primary_anchor.source})={primary_value} "
                                f"与支撑来源({anchor.source})={support_value} 差异{diff_pct:.1f}%"
                            )
        
        return issues
    
    def _parse_number(self, value: str) -> Optional[float]:
        """解析数字"""
        try:
            # 移除非数字字符
            clean = re.sub(r'[^\d.]', '', str(value))
            return float(clean) if clean else None
        except:
            return None
    
    def generate_data_quality_report(self) -> str:
        """生成数据质量报告"""
        result = "## 数据质量报告\n\n"
        
        # 统计各层级数据
        tier_counts = {tier: 0 for tier in DataSourceTier}
        total_confidence = 0
        
        for dp in self.data_points.values():
            tier_counts[dp.primary_anchor.source_tier] += 1
            total_confidence += dp.get_confidence_score()
        
        total = len(self.data_points)
        if total == 0:
            return result + "暂无数据点\n"
        
        # 来源层级分布
        result += "### 数据来源层级分布\n\n"
        result += "| 层级 | 数量 | 占比 |\n"
        result += "|------|------|------|\n"
        for tier, count in tier_counts.items():
            pct = count / total * 100 if total > 0 else 0
            result += f"| {tier.value} | {count} | {pct:.1f}% |\n"
        
        # 平均置信度
        avg_confidence = total_confidence / total if total > 0 else 0
        result += f"\n### 综合数据质量评分：{avg_confidence:.0%}\n"
        
        # 一致性检查
        issues = self.validate_data_consistency()
        if issues:
            result += "\n### 数据一致性问题\n\n"
            for issue in issues:
                result += f"- {issue}\n"
        else:
            result += "\n### 数据一致性：✅ 通过\n"
        
        return result


# 专业数据引用模板
DATA_CITATION_TEMPLATES = {
    "market_size": """
**{metric_name}**：{value}{unit}

**数据拆解**：
{breakdown}

**来源说明**：
- 主要来源：{primary_source}（{source_tier}）
- 数据日期：{date}
- 测算方法：{methodology}

**交叉验证**：{cross_validation}
""",
    
    "growth_rate": """
**{metric_name}**：{value}

**推导过程**：
{derivation}

**数据来源**：{source}（{date}）
**预测假设**：{assumptions}
""",
    
    "company_data": """
**{company_name} - {metric_name}**：{value}{unit}

**数据来源**：{source}
**披露日期**：{date}
**财报期间**：{period}
**计算口径**：{calculation_basis}
"""
}


# 创建全局实例
data_anchoring_framework = DataAnchoringFramework()


# Prompt模板：锚定型数据收集
ANCHORED_DATA_COLLECTION_PROMPT = """
【锚定型数据收集要求】

你正在进行专业级行业研究，所有数据必须符合"锚定型"标准：

## 一、数据来源层级要求

| 层级 | 来源类型 | 可信度 | 使用场景 |
|------|----------|--------|----------|
| 一级 | 官方统计、上市公司公告 | 最高 | 核心数据必须使用 |
| 二级 | 权威研究机构、行业协会 | 高 | 补充数据可使用 |
| 三级 | 媒体报道、专家访谈 | 中 | 定性判断参考 |
| 四级 | 推算、估计 | 低 | 必须说明推算逻辑 |

## 二、核心数据必须包含

1. **市场规模数据**
   - 必须有一级来源锚点
   - 必须拆解到细分市场
   - 示例格式：
   > "2025E 浙江 AI 核心产业规模 1130 亿元，其中：
   > - 工业 AI：380 亿元（基于海康威视、大华股份等 12 家上市公司披露收入外推）
   > - AI 云服务：290 亿元（阿里云浙江区域收入，来源：阿里巴巴 2024 年报）
   > - 智能安防：260 亿元（海康/大华浙江区域收入拆分，来源：公司年报）
   > - 其他：200 亿元（省统计局数据差额）"

2. **增长率数据**
   - 必须说明计算方法（CAGR/同比/环比）
   - 必须有历史数据支撑
   - 预测数据必须说明假设

3. **竞争格局数据**
   - 市场份额必须标注来源
   - CR5/CR10 必须列出具体企业
   - 示例格式：
   > "浙江 AI 安防市场 CR2 达 65%
   > - 海康威视：约 40%（2024 年报披露浙江区域收入 / 省统计局行业总产值）
   > - 大华股份：约 25%（同上方法测算）"

## 三、数据引用格式

每个关键数据必须按以下格式引用：

```
【数据点】市场规模
【数值】1130 亿元
【来源】浙江省统计局《2024 年数字经济发展报告》
【来源层级】一级来源
【日期】2024 年 12 月
【测算方法】直接引用官方统计
【置信度】95%
```

## 四、禁止事项

❌ 禁止使用没有来源的数据
❌ 禁止使用"据估计"、"大约"等模糊表述作为核心数据
❌ 禁止不同章节使用同一指标的不同数值
❌ 禁止使用超过 2 年的过时数据作为当前数据

## 五、数据质量自检

完成数据收集后，必须回答：
1. 核心数据（市场规模、增长率）是否都有一级来源？
2. 数据拆解是否可以验证总和？
3. 不同来源的同一数据是否一致？
4. 预测数据的假设是否合理？
"""


def get_anchored_data_prompt(industry: str, province: str, year: str) -> str:
    """获取锚定型数据收集Prompt"""
    return f"""
{ANCHORED_DATA_COLLECTION_PROMPT}

【本次研究任务】
- 行业：{industry}
- 区域：{province}
- 目标年份：{year}

【必须锚定的核心数据】
1. {province}{industry}市场总规模（一级来源）
2. 细分市场规模拆解（至少 4 个细分）
3. 历史增长率（近 3-5 年）
4. 预测增长率（未来 3 年）
5. 市场集中度（CR5，含具体企业）
6. 龙头企业收入/利润（上市公司年报）

请严格按照锚定型数据标准收集和呈现数据。
"""
