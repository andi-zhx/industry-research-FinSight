# agent_system/professional/micro_risk_analysis.py
"""
项目级微观风险分析模块
解决差距四：风险仍偏行业风险，而非"项目级风险"

核心理念：
- 不只是"政策、技术、竞争、合规"等宏观风险
- 而是"投后视角的微观风险"
- 包含：技术失败概率、客户集中度、团队风险、执行风险等
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class RiskCategory(Enum):
    """风险类别"""
    TECHNOLOGY = "技术风险"
    MARKET = "市场风险"
    COMPETITION = "竞争风险"
    EXECUTION = "执行风险"
    FINANCIAL = "财务风险"
    REGULATORY = "监管风险"
    TEAM = "团队风险"
    CUSTOMER = "客户风险"
    SUPPLY_CHAIN = "供应链风险"
    GEOPOLITICAL = "地缘政治风险"


class RiskLevel(Enum):
    """风险等级"""
    CRITICAL = "致命风险"
    HIGH = "高风险"
    MEDIUM = "中等风险"
    LOW = "低风险"


class RiskTrend(Enum):
    """风险趋势"""
    INCREASING = "上升"
    STABLE = "稳定"
    DECREASING = "下降"


@dataclass
class MicroRisk:
    """微观风险"""
    risk_name: str              # 风险名称
    category: RiskCategory      # 风险类别
    level: RiskLevel            # 风险等级
    probability: float          # 发生概率 0-1
    impact: float               # 影响程度 0-1
    trend: RiskTrend            # 趋势
    
    # 详细描述
    description: str = ""       # 风险描述
    trigger_conditions: List[str] = field(default_factory=list)  # 触发条件
    warning_signs: List[str] = field(default_factory=list)  # 预警信号
    
    # 量化指标
    quantified_impact: str = ""  # 量化影响（如：收入下降XX%）
    time_horizon: str = ""       # 时间范围
    
    # 应对措施
    mitigation_measures: List[str] = field(default_factory=list)  # 缓解措施
    contingency_plan: str = ""   # 应急预案
    
    # 监控指标
    monitoring_kpis: List[str] = field(default_factory=list)  # 监控KPI
    
    def get_risk_score(self) -> float:
        """计算风险得分"""
        return self.probability * self.impact * 100
    
    def get_risk_matrix_position(self) -> Tuple[str, str]:
        """获取风险矩阵位置"""
        prob_level = "高" if self.probability > 0.6 else ("中" if self.probability > 0.3 else "低")
        impact_level = "高" if self.impact > 0.6 else ("中" if self.impact > 0.3 else "低")
        return (prob_level, impact_level)


@dataclass
class IndustryChainRisk:
    """产业链环节风险"""
    chain_position: str         # 产业链位置（上游/中游/下游）
    segment_name: str           # 细分环节
    
    # 环节特有风险
    specific_risks: List[MicroRisk] = field(default_factory=list)
    
    # 量化指标
    tape_out_failure_rate: float = 0  # 流片失败率（芯片）
    customer_concentration: float = 0  # 客户集中度
    supplier_concentration: float = 0  # 供应商集中度
    renewal_rate: float = 0           # 续费率（SaaS）
    project_to_product_rate: float = 0  # 项目转产品成功率
    
    def get_chain_risk_summary(self) -> str:
        """获取产业链风险摘要"""
        summary = f"**{self.chain_position} - {self.segment_name}**\n\n"
        
        if self.tape_out_failure_rate > 0:
            summary += f"- 流片失败率：{self.tape_out_failure_rate:.0%}\n"
        if self.customer_concentration > 0:
            summary += f"- 客户集中度（CR5）：{self.customer_concentration:.0%}\n"
        if self.supplier_concentration > 0:
            summary += f"- 供应商集中度（CR5）：{self.supplier_concentration:.0%}\n"
        if self.renewal_rate > 0:
            summary += f"- 客户续费率：{self.renewal_rate:.0%}\n"
        if self.project_to_product_rate > 0:
            summary += f"- 项目转产品成功率：{self.project_to_product_rate:.0%}\n"
        
        return summary


@dataclass
class ProjectRiskProfile:
    """项目风险画像"""
    project_name: str
    industry: str
    investment_stage: str
    
    # 微观风险列表
    micro_risks: List[MicroRisk] = field(default_factory=list)
    
    # 产业链风险
    chain_risks: List[IndustryChainRisk] = field(default_factory=list)
    
    # 综合评估
    overall_risk_score: float = 0
    risk_adjusted_return: float = 0
    
    def calculate_overall_risk(self) -> float:
        """计算综合风险得分"""
        if not self.micro_risks:
            return 0
        
        # 加权平均（致命风险权重更高）
        weights = {
            RiskLevel.CRITICAL: 3.0,
            RiskLevel.HIGH: 2.0,
            RiskLevel.MEDIUM: 1.0,
            RiskLevel.LOW: 0.5
        }
        
        total_weighted_score = 0
        total_weight = 0
        
        for risk in self.micro_risks:
            weight = weights.get(risk.level, 1.0)
            total_weighted_score += risk.get_risk_score() * weight
            total_weight += weight
        
        self.overall_risk_score = total_weighted_score / total_weight if total_weight > 0 else 0
        return self.overall_risk_score
    
    def get_critical_risks(self) -> List[MicroRisk]:
        """获取致命风险"""
        return [r for r in self.micro_risks if r.level == RiskLevel.CRITICAL]
    
    def get_high_risks(self) -> List[MicroRisk]:
        """获取高风险"""
        return [r for r in self.micro_risks if r.level == RiskLevel.HIGH]
    
    def generate_risk_report(self) -> str:
        """生成风险报告"""
        report = f"# {self.project_name} 项目级风险分析\n\n"
        report += f"**行业**：{self.industry}\n"
        report += f"**投资阶段**：{self.investment_stage}\n\n"
        
        # 风险概览
        self.calculate_overall_risk()
        report += "## 一、风险概览\n\n"
        report += f"**综合风险得分**：{self.overall_risk_score:.1f}/100\n\n"
        
        # 风险分布
        risk_counts = {}
        for risk in self.micro_risks:
            level = risk.level.value
            risk_counts[level] = risk_counts.get(level, 0) + 1
        
        report += "| 风险等级 | 数量 |\n"
        report += "|----------|------|\n"
        for level, count in risk_counts.items():
            report += f"| {level} | {count} |\n"
        report += "\n"
        
        # 致命风险
        critical_risks = self.get_critical_risks()
        if critical_risks:
            report += "## 二、致命风险（必须关注）\n\n"
            for risk in critical_risks:
                report += self._format_risk_detail(risk)
        
        # 高风险
        high_risks = self.get_high_risks()
        if high_risks:
            report += "## 三、高风险\n\n"
            for risk in high_risks:
                report += self._format_risk_detail(risk)
        
        # 产业链风险
        if self.chain_risks:
            report += "## 四、产业链环节风险\n\n"
            for chain_risk in self.chain_risks:
                report += chain_risk.get_chain_risk_summary()
                report += "\n"
        
        # 风险矩阵
        report += "## 五、风险矩阵\n\n"
        report += self._generate_risk_matrix()
        
        # 监控建议
        report += "## 六、风险监控建议\n\n"
        report += self._generate_monitoring_recommendations()
        
        return report
    
    def _format_risk_detail(self, risk: MicroRisk) -> str:
        """格式化风险详情"""
        result = f"### {risk.risk_name}\n\n"
        result += f"- **类别**：{risk.category.value}\n"
        result += f"- **等级**：{risk.level.value}\n"
        result += f"- **概率**：{risk.probability:.0%}\n"
        result += f"- **影响**：{risk.impact:.0%}\n"
        result += f"- **趋势**：{risk.trend.value}\n\n"
        
        if risk.description:
            result += f"**描述**：{risk.description}\n\n"
        
        if risk.quantified_impact:
            result += f"**量化影响**：{risk.quantified_impact}\n\n"
        
        if risk.trigger_conditions:
            result += "**触发条件**：\n"
            for cond in risk.trigger_conditions:
                result += f"- {cond}\n"
            result += "\n"
        
        if risk.warning_signs:
            result += "**预警信号**：\n"
            for sign in risk.warning_signs:
                result += f"- {sign}\n"
            result += "\n"
        
        if risk.mitigation_measures:
            result += "**缓解措施**：\n"
            for measure in risk.mitigation_measures:
                result += f"- {measure}\n"
            result += "\n"
        
        return result
    
    def _generate_risk_matrix(self) -> str:
        """生成风险矩阵"""
        matrix = """
```
        影响程度
        低      中      高
概 高  [     ] [     ] [     ]
率 中  [     ] [     ] [     ]
   低  [     ] [     ] [     ]
```
"""
        # 填充风险
        positions = {}
        for risk in self.micro_risks:
            pos = risk.get_risk_matrix_position()
            key = f"{pos[0]}-{pos[1]}"
            if key not in positions:
                positions[key] = []
            positions[key].append(risk.risk_name[:4])
        
        result = "| 概率\\影响 | 低 | 中 | 高 |\n"
        result += "|-----------|-----|-----|-----|\n"
        
        for prob in ["高", "中", "低"]:
            row = f"| {prob} |"
            for impact in ["低", "中", "高"]:
                key = f"{prob}-{impact}"
                risks = positions.get(key, [])
                row += f" {', '.join(risks[:2]) if risks else '-'} |"
            result += row + "\n"
        
        return result + "\n"
    
    def _generate_monitoring_recommendations(self) -> str:
        """生成监控建议"""
        result = ""
        
        # 收集所有监控KPI
        all_kpis = []
        for risk in self.micro_risks:
            all_kpis.extend(risk.monitoring_kpis)
        
        if all_kpis:
            result += "### 关键监控指标\n\n"
            for kpi in list(set(all_kpis))[:10]:
                result += f"- {kpi}\n"
            result += "\n"
        
        # 监控频率建议
        result += "### 监控频率建议\n\n"
        result += "| 风险类别 | 建议频率 |\n"
        result += "|----------|----------|\n"
        result += "| 致命风险 | 每周 |\n"
        result += "| 高风险 | 每两周 |\n"
        result += "| 中等风险 | 每月 |\n"
        result += "| 低风险 | 每季度 |\n"
        
        return result


class MicroRiskAnalyzer:
    """微观风险分析器"""
    
    # 产业链环节典型风险
    CHAIN_SEGMENT_RISKS = {
        "上游-芯片设计": {
            "tape_out_failure_rate": 0.3,  # 流片失败率30%
            "typical_risks": [
                ("EDA工具受限", RiskLevel.CRITICAL, 0.7, 0.9),
                ("流片失败", RiskLevel.HIGH, 0.3, 0.8),
                ("IP核授权风险", RiskLevel.MEDIUM, 0.4, 0.5),
                ("人才流失", RiskLevel.HIGH, 0.5, 0.6)
            ]
        },
        "上游-算力基础设施": {
            "supplier_concentration": 0.8,  # 供应商集中度80%
            "typical_risks": [
                ("GPU供应受限", RiskLevel.CRITICAL, 0.8, 0.9),
                ("能耗成本上升", RiskLevel.MEDIUM, 0.6, 0.4),
                ("技术迭代风险", RiskLevel.HIGH, 0.5, 0.7)
            ]
        },
        "中游-AI平台": {
            "customer_concentration": 0.5,
            "typical_risks": [
                ("被云厂商内部团队替代", RiskLevel.HIGH, 0.4, 0.8),
                ("大模型压缩中游价值", RiskLevel.HIGH, 0.5, 0.7),
                ("客户集中度过高", RiskLevel.MEDIUM, 0.5, 0.5),
                ("定价权弱", RiskLevel.MEDIUM, 0.6, 0.4)
            ]
        },
        "中游-模型服务": {
            "renewal_rate": 0.7,
            "typical_risks": [
                ("模型同质化", RiskLevel.HIGH, 0.6, 0.6),
                ("开源模型冲击", RiskLevel.HIGH, 0.7, 0.5),
                ("算力成本居高不下", RiskLevel.MEDIUM, 0.5, 0.5)
            ]
        },
        "下游-行业应用": {
            "project_to_product_rate": 0.3,  # 项目转产品成功率30%
            "typical_risks": [
                ("项目制陷阱", RiskLevel.HIGH, 0.6, 0.6),
                ("客户续费率低", RiskLevel.HIGH, 0.5, 0.7),
                ("交付周期长", RiskLevel.MEDIUM, 0.6, 0.4),
                ("定制化程度高", RiskLevel.MEDIUM, 0.7, 0.4)
            ]
        }
    }
    
    def __init__(self):
        pass
    
    def analyze_chain_segment_risk(self, segment: str) -> IndustryChainRisk:
        """分析产业链环节风险"""
        
        segment_data = self.CHAIN_SEGMENT_RISKS.get(segment, {})
        
        chain_risk = IndustryChainRisk(
            chain_position=segment.split("-")[0] if "-" in segment else segment,
            segment_name=segment.split("-")[1] if "-" in segment else segment,
            tape_out_failure_rate=segment_data.get("tape_out_failure_rate", 0),
            customer_concentration=segment_data.get("customer_concentration", 0),
            supplier_concentration=segment_data.get("supplier_concentration", 0),
            renewal_rate=segment_data.get("renewal_rate", 0),
            project_to_product_rate=segment_data.get("project_to_product_rate", 0)
        )
        
        # 添加典型风险
        for risk_data in segment_data.get("typical_risks", []):
            risk = MicroRisk(
                risk_name=risk_data[0],
                category=RiskCategory.TECHNOLOGY,
                level=risk_data[1],
                probability=risk_data[2],
                impact=risk_data[3],
                trend=RiskTrend.STABLE
            )
            chain_risk.specific_risks.append(risk)
        
        return chain_risk
    
    def create_project_risk_profile(
        self,
        project_name: str,
        industry: str,
        investment_stage: str,
        chain_segments: List[str],
        custom_risks: List[Dict] = None
    ) -> ProjectRiskProfile:
        """创建项目风险画像"""
        
        profile = ProjectRiskProfile(
            project_name=project_name,
            industry=industry,
            investment_stage=investment_stage
        )
        
        # 分析产业链风险
        for segment in chain_segments:
            chain_risk = self.analyze_chain_segment_risk(segment)
            profile.chain_risks.append(chain_risk)
            
            # 将产业链风险添加到微观风险列表
            profile.micro_risks.extend(chain_risk.specific_risks)
        
        # 添加自定义风险
        if custom_risks:
            for cr in custom_risks:
                risk = MicroRisk(
                    risk_name=cr.get("name", ""),
                    category=RiskCategory[cr.get("category", "TECHNOLOGY")],
                    level=RiskLevel[cr.get("level", "MEDIUM")],
                    probability=cr.get("probability", 0.5),
                    impact=cr.get("impact", 0.5),
                    trend=RiskTrend[cr.get("trend", "STABLE")],
                    description=cr.get("description", ""),
                    quantified_impact=cr.get("quantified_impact", ""),
                    mitigation_measures=cr.get("mitigation_measures", [])
                )
                profile.micro_risks.append(risk)
        
        return profile


# 创建全局实例
micro_risk_analyzer = MicroRiskAnalyzer()


# Prompt模板：项目级风险分析
MICRO_RISK_PROMPT = """
【项目级微观风险分析要求】

你正在进行专业级投资风险分析，需要"投后视角的微观风险"：

## 一、产业链环节风险（必须）

针对目标所在的产业链环节，分析特有风险：

### 上游（芯片/算力）
- 流片失败率：XX%（行业平均30%）
- EDA工具受限影响
- GPU供应受限影响
- 技术迭代风险

### 中游（平台/模型）
- 被云厂商内部团队替代风险
- 大模型压缩中游价值风险
- 客户集中度：CR5=XX%
- 定价权分析

### 下游（应用）
- 项目转产品成功率：XX%（行业平均30%）
- 客户续费率：XX%
- 交付周期
- 定制化程度

## 二、微观风险清单（必须）

每个风险必须包含：

| 风险名称 | 类别 | 等级 | 概率 | 影响 | 趋势 |
|----------|------|------|------|------|------|
| | | 致命/高/中/低 | XX% | XX% | 上升/稳定/下降 |

### 风险详情模板

**风险名称**：XXX
- **类别**：技术/市场/竞争/执行/财务/监管/团队/客户/供应链
- **等级**：致命/高/中/低
- **概率**：XX%
- **影响**：XX%
- **量化影响**：如发生，预计收入下降XX%/成本上升XX%
- **触发条件**：
  - 条件1
  - 条件2
- **预警信号**：
  - 信号1
  - 信号2
- **缓解措施**：
  - 措施1
  - 措施2
- **监控KPI**：
  - KPI1
  - KPI2

## 三、致命风险专项分析（如有）

对于致命风险，必须深入分析：
1. 发生的具体场景
2. 对投资回报的影响测算
3. 是否有对冲/保护措施
4. 投资条款中的保护条款建议

## 四、风险矩阵

```
        影响程度
        低      中      高
概 高  [     ] [     ] [致命区]
率 中  [     ] [关注区] [     ]
   低  [     ] [     ] [     ]
```

## 五、风险监控建议

| 风险类别 | 监控指标 | 监控频率 | 预警阈值 |
|----------|----------|----------|----------|
| | | | |

---

**PE投后视角关键问题**：
1. 上游芯片：Tape-out失败概率？EDA受限具体影响？
2. 中游平台：客户集中度？是否被阿里云内部团队替代？
3. 下游应用：客户续费率？项目转产品失败率？
"""


def get_micro_risk_prompt(project_name: str, industry: str, chain_position: str) -> str:
    """获取微观风险分析Prompt"""
    return f"""
{MICRO_RISK_PROMPT}

【本次分析任务】
- 项目名称：{project_name}
- 所属行业：{industry}
- 产业链位置：{chain_position}

请按照上述框架进行项目级微观风险分析，确保：
1. 分析产业链环节特有风险
2. 每个风险有量化的概率和影响
3. 致命风险有专项分析
4. 提供具体的监控KPI和预警阈值
"""
