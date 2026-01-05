# agent_system/professional/pe_report_scorer.py
"""
PE级行业研报评分与补强清单
提供专业级研报质量评估和改进建议

评分维度：
1. 数据可信度（锚定型数据）
2. 标的深拆（公司级分析）
3. 估值与回报（财务投资语言）
4. 风险分析（项目级微观风险）
5. 观点差异化（反共识判断）
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re


class ReportLevel(Enum):
    """研报等级"""
    L1 = "L1-基础行研"      # 三四线券商/咨询公司模板
    L2 = "L2-主流行研"      # 主流券商行业分析师常规报告
    L3 = "L3-专业行研"      # 一线PE/产业资本内部研究
    L4 = "L4-顶级行研"      # 头部PE/一线券商首席级深度报告


class ScoreDimension(Enum):
    """评分维度"""
    DATA_CREDIBILITY = "数据可信度"
    COMPANY_DEEP_DIVE = "标的深拆"
    VALUATION_RETURN = "估值与回报"
    RISK_ANALYSIS = "风险分析"
    CONTRARIAN_VIEWS = "观点差异化"
    INVESTMENT_ORIENTATION = "投资导向"
    WRITING_QUALITY = "写作质量"


@dataclass
class DimensionScore:
    """维度评分"""
    dimension: ScoreDimension
    score: float                # 0-100
    weight: float               # 权重
    strengths: List[str] = field(default_factory=list)  # 优点
    weaknesses: List[str] = field(default_factory=list)  # 不足
    improvements: List[str] = field(default_factory=list)  # 改进建议
    
    def get_weighted_score(self) -> float:
        return self.score * self.weight


@dataclass
class ReportScoreCard:
    """研报评分卡"""
    report_title: str
    dimension_scores: List[DimensionScore] = field(default_factory=list)
    overall_score: float = 0
    report_level: ReportLevel = ReportLevel.L2
    
    # 关键缺失
    critical_gaps: List[str] = field(default_factory=list)
    
    # 补强清单
    enhancement_checklist: List[Dict] = field(default_factory=list)
    
    def calculate_overall_score(self):
        """计算综合得分"""
        if not self.dimension_scores:
            return
        
        total_weighted = sum(ds.get_weighted_score() for ds in self.dimension_scores)
        total_weight = sum(ds.weight for ds in self.dimension_scores)
        
        self.overall_score = total_weighted / total_weight if total_weight > 0 else 0
        
        # 确定等级
        if self.overall_score >= 85:
            self.report_level = ReportLevel.L4
        elif self.overall_score >= 70:
            self.report_level = ReportLevel.L3
        elif self.overall_score >= 55:
            self.report_level = ReportLevel.L2
        else:
            self.report_level = ReportLevel.L1
    
    def generate_scorecard_report(self) -> str:
        """生成评分报告"""
        self.calculate_overall_score()
        
        report = f"# {self.report_title} 质量评估报告\n\n"
        
        # 总体评分
        report += "## 一、总体评分\n\n"
        report += f"**综合得分**：{self.overall_score:.1f}/100\n\n"
        report += f"**研报等级**：{self.report_level.value}\n\n"
        
        # 等级说明
        report += "| 等级 | 说明 | 分数区间 |\n"
        report += "|------|------|----------|\n"
        report += "| L4-顶级行研 | 头部PE/一线券商首席级 | 85+ |\n"
        report += "| L3-专业行研 | 一线PE/产业资本内部研究 | 70-84 |\n"
        report += "| L2-主流行研 | 主流券商行业分析师 | 55-69 |\n"
        report += "| L1-基础行研 | 三四线券商/咨询公司 | <55 |\n\n"
        
        # 维度评分
        report += "## 二、维度评分\n\n"
        report += "| 维度 | 得分 | 权重 | 加权得分 |\n"
        report += "|------|------|------|----------|\n"
        
        for ds in self.dimension_scores:
            weighted = ds.get_weighted_score()
            report += f"| {ds.dimension.value} | {ds.score:.0f} | {ds.weight:.0%} | {weighted:.1f} |\n"
        
        report += "\n"
        
        # 各维度详情
        report += "## 三、各维度详情\n\n"
        
        for ds in self.dimension_scores:
            report += f"### {ds.dimension.value}（{ds.score:.0f}分）\n\n"
            
            if ds.strengths:
                report += "**优点**：\n"
                for s in ds.strengths:
                    report += f"- ✅ {s}\n"
                report += "\n"
            
            if ds.weaknesses:
                report += "**不足**：\n"
                for w in ds.weaknesses:
                    report += f"- ❌ {w}\n"
                report += "\n"
            
            if ds.improvements:
                report += "**改进建议**：\n"
                for i in ds.improvements:
                    report += f"- 💡 {i}\n"
                report += "\n"
        
        # 关键缺失
        if self.critical_gaps:
            report += "## 四、关键缺失（必须补齐）\n\n"
            for i, gap in enumerate(self.critical_gaps, 1):
                report += f"{i}. ⚠️ {gap}\n"
            report += "\n"
        
        # 补强清单
        if self.enhancement_checklist:
            report += "## 五、补强清单\n\n"
            report += "| 优先级 | 补强项 | 预期提升 | 工作量 |\n"
            report += "|--------|--------|----------|--------|\n"
            
            for item in self.enhancement_checklist:
                report += f"| {item['priority']} | {item['item']} | +{item['score_boost']}分 | {item['effort']} |\n"
        
        return report


class PEReportScorer:
    """PE级研报评分器"""
    
    # 评分标准
    SCORING_CRITERIA = {
        ScoreDimension.DATA_CREDIBILITY: {
            "weight": 0.25,
            "criteria": {
                "tier1_data_ratio": "一级来源数据占比",
                "data_breakdown": "数据拆解完整性",
                "cross_validation": "交叉验证",
                "source_citation": "来源标注规范性"
            },
            "max_scores": {
                "tier1_data_ratio": 30,
                "data_breakdown": 30,
                "cross_validation": 20,
                "source_citation": 20
            }
        },
        ScoreDimension.COMPANY_DEEP_DIVE: {
            "weight": 0.20,
            "criteria": {
                "revenue_breakdown": "收入结构拆解",
                "financial_analysis": "财务深度分析",
                "competitive_comparison": "竞争对比量化",
                "ai_analysis": "AI相关分析"
            },
            "max_scores": {
                "revenue_breakdown": 30,
                "financial_analysis": 30,
                "competitive_comparison": 25,
                "ai_analysis": 15
            }
        },
        ScoreDimension.VALUATION_RETURN: {
            "weight": 0.20,
            "criteria": {
                "valuation_methods": "估值方法多样性",
                "return_scenarios": "回报情景分析",
                "irr_moic": "IRR/MOIC计算",
                "investor_fit": "投资者适配"
            },
            "max_scores": {
                "valuation_methods": 30,
                "return_scenarios": 30,
                "irr_moic": 25,
                "investor_fit": 15
            }
        },
        ScoreDimension.RISK_ANALYSIS: {
            "weight": 0.15,
            "criteria": {
                "micro_risks": "微观风险识别",
                "quantified_risks": "风险量化",
                "chain_risks": "产业链风险",
                "monitoring_kpis": "监控指标"
            },
            "max_scores": {
                "micro_risks": 30,
                "quantified_risks": 30,
                "chain_risks": 25,
                "monitoring_kpis": 15
            }
        },
        ScoreDimension.CONTRARIAN_VIEWS: {
            "weight": 0.10,
            "criteria": {
                "consensus_identification": "共识识别",
                "contrarian_arguments": "反共识论证",
                "evidence_support": "证据支撑",
                "investment_implications": "投资含义"
            },
            "max_scores": {
                "consensus_identification": 25,
                "contrarian_arguments": 35,
                "evidence_support": 25,
                "investment_implications": 15
            }
        },
        ScoreDimension.INVESTMENT_ORIENTATION: {
            "weight": 0.05,
            "criteria": {
                "tam_analysis": "TAM分析",
                "value_chain": "价值链分配",
                "exit_path": "退出路径",
                "investor_type_fit": "投资者类型适配"
            },
            "max_scores": {
                "tam_analysis": 25,
                "value_chain": 30,
                "exit_path": 25,
                "investor_type_fit": 20
            }
        },
        ScoreDimension.WRITING_QUALITY: {
            "weight": 0.05,
            "criteria": {
                "logic_flow": "逻辑流畅性",
                "professional_language": "专业语言",
                "no_ai_slop": "无AI水文",
                "actionable": "可操作性"
            },
            "max_scores": {
                "logic_flow": 25,
                "professional_language": 25,
                "no_ai_slop": 25,
                "actionable": 25
            }
        }
    }
    
    def __init__(self):
        pass
    
    def score_report(self, report_content: str, report_title: str = "行业研究报告") -> ReportScoreCard:
        """评分研报"""
        
        scorecard = ReportScoreCard(report_title=report_title)
        
        # 评估各维度
        for dimension, config in self.SCORING_CRITERIA.items():
            ds = self._score_dimension(report_content, dimension, config)
            scorecard.dimension_scores.append(ds)
        
        # 识别关键缺失
        scorecard.critical_gaps = self._identify_critical_gaps(report_content)
        
        # 生成补强清单
        scorecard.enhancement_checklist = self._generate_enhancement_checklist(scorecard)
        
        # 计算总分
        scorecard.calculate_overall_score()
        
        return scorecard
    
    def _score_dimension(
        self,
        content: str,
        dimension: ScoreDimension,
        config: Dict
    ) -> DimensionScore:
        """评估单个维度"""
        
        score = 0
        strengths = []
        weaknesses = []
        improvements = []
        
        criteria = config["criteria"]
        max_scores = config["max_scores"]
        
        # 数据可信度评估
        if dimension == ScoreDimension.DATA_CREDIBILITY:
            # 检查一级来源
            tier1_keywords = ["统计局", "年报", "公告", "Wind", "Bloomberg", "央行", "证监会"]
            tier1_count = sum(1 for kw in tier1_keywords if kw in content)
            if tier1_count >= 5:
                score += max_scores["tier1_data_ratio"]
                strengths.append("使用了多个一级数据来源")
            elif tier1_count >= 2:
                score += max_scores["tier1_data_ratio"] * 0.6
                weaknesses.append("一级数据来源不够充分")
                improvements.append("增加官方统计和上市公司公告引用")
            else:
                score += max_scores["tier1_data_ratio"] * 0.3
                weaknesses.append("缺少一级数据来源")
                improvements.append("必须补充官方统计和上市公司年报数据")
            
            # 检查数据拆解
            if "拆解" in content or "细分" in content or "其中：" in content:
                score += max_scores["data_breakdown"]
                strengths.append("有数据拆解")
            else:
                weaknesses.append("缺少数据拆解")
                improvements.append("对市场规模等核心数据进行细分拆解")
            
            # 检查交叉验证
            if "验证" in content or "对比" in content:
                score += max_scores["cross_validation"]
            else:
                weaknesses.append("缺少交叉验证")
                improvements.append("对关键数据进行多来源交叉验证")
            
            # 检查来源标注
            if "来源：" in content or "数据来源" in content:
                score += max_scores["source_citation"]
                strengths.append("有来源标注")
            else:
                weaknesses.append("来源标注不规范")
                improvements.append("为每个关键数据标注来源")
        
        # 标的深拆评估
        elif dimension == ScoreDimension.COMPANY_DEEP_DIVE:
            # 检查收入结构
            if "收入结构" in content or "业务板块" in content or "营收占比" in content:
                score += max_scores["revenue_breakdown"]
                strengths.append("有收入结构分析")
            else:
                weaknesses.append("缺少收入结构拆解")
                improvements.append("添加重点公司的收入结构拆解")
            
            # 检查财务分析
            financial_keywords = ["ROE", "毛利率", "净利率", "杜邦", "现金流"]
            financial_count = sum(1 for kw in financial_keywords if kw in content)
            if financial_count >= 3:
                score += max_scores["financial_analysis"]
                strengths.append("财务分析深入")
            elif financial_count >= 1:
                score += max_scores["financial_analysis"] * 0.5
                weaknesses.append("财务分析不够深入")
                improvements.append("添加杜邦分析和现金流分析")
            else:
                weaknesses.append("缺少财务深度分析")
                improvements.append("必须添加核心财务指标分析")
            
            # 检查竞争对比
            if "竞争对比" in content or "vs" in content.lower() or "对比" in content:
                score += max_scores["competitive_comparison"]
                strengths.append("有竞争对比")
            else:
                weaknesses.append("缺少量化竞争对比")
                improvements.append("添加与竞争对手的量化对比表格")
            
            # 检查AI分析
            if "AI" in content and ("占比" in content or "收入" in content):
                score += max_scores["ai_analysis"]
        
        # 估值与回报评估
        elif dimension == ScoreDimension.VALUATION_RETURN:
            # 检查估值方法
            valuation_keywords = ["PE", "PB", "PS", "DCF", "EV/EBITDA"]
            valuation_count = sum(1 for kw in valuation_keywords if kw in content)
            if valuation_count >= 3:
                score += max_scores["valuation_methods"]
                strengths.append("使用多种估值方法")
            elif valuation_count >= 1:
                score += max_scores["valuation_methods"] * 0.5
                weaknesses.append("估值方法单一")
                improvements.append("使用至少2-3种估值方法交叉验证")
            else:
                weaknesses.append("缺少估值分析")
                improvements.append("必须添加估值锚点分析")
            
            # 检查回报情景
            if "情景" in content or "乐观" in content or "悲观" in content:
                score += max_scores["return_scenarios"]
                strengths.append("有情景分析")
            else:
                weaknesses.append("缺少回报情景分析")
                improvements.append("添加乐观/中性/悲观三种情景")
            
            # 检查IRR/MOIC
            if "IRR" in content or "MOIC" in content or "回报率" in content:
                score += max_scores["irr_moic"]
                strengths.append("有IRR/MOIC计算")
            else:
                weaknesses.append("缺少IRR/MOIC计算")
                improvements.append("添加投资回报率测算")
            
            # 检查投资者适配
            if "VC" in content or "PE" in content or "产业资本" in content:
                score += max_scores["investor_fit"]
        
        # 风险分析评估
        elif dimension == ScoreDimension.RISK_ANALYSIS:
            # 检查微观风险
            micro_risk_keywords = ["流片失败", "客户集中度", "续费率", "项目转产品"]
            micro_count = sum(1 for kw in micro_risk_keywords if kw in content)
            if micro_count >= 2:
                score += max_scores["micro_risks"]
                strengths.append("有微观风险分析")
            elif "风险" in content:
                score += max_scores["micro_risks"] * 0.5
                weaknesses.append("风险分析偏宏观")
                improvements.append("添加项目级微观风险")
            else:
                weaknesses.append("缺少风险分析")
                improvements.append("必须添加风险分析章节")
            
            # 检查风险量化
            if "概率" in content or "%" in content:
                score += max_scores["quantified_risks"]
            else:
                weaknesses.append("风险未量化")
                improvements.append("为每个风险添加概率和影响评估")
            
            # 检查产业链风险
            if "上游" in content and "风险" in content:
                score += max_scores["chain_risks"]
            
            # 检查监控指标
            if "监控" in content or "KPI" in content:
                score += max_scores["monitoring_kpis"]
        
        # 反共识观点评估
        elif dimension == ScoreDimension.CONTRARIAN_VIEWS:
            # 检查共识识别
            if "市场普遍认为" in content or "共识" in content:
                score += max_scores["consensus_identification"]
                strengths.append("识别了市场共识")
            else:
                weaknesses.append("未明确市场共识")
                improvements.append("先明确市场主流观点")
            
            # 检查反共识论证
            if "我们认为" in content and ("不同" in content or "错误" in content):
                score += max_scores["contrarian_arguments"]
                strengths.append("有反共识判断")
            else:
                weaknesses.append("缺少反共识观点")
                improvements.append("添加1-2个与市场不同的判断")
            
            # 检查证据支撑
            if "证据" in content or "数据支撑" in content:
                score += max_scores["evidence_support"]
            
            # 检查投资含义
            if "投资含义" in content or "投资建议" in content:
                score += max_scores["investment_implications"]
        
        # 投资导向评估
        elif dimension == ScoreDimension.INVESTMENT_ORIENTATION:
            if "TAM" in content or "市场规模" in content:
                score += max_scores["tam_analysis"]
                strengths.append("有TAM分析")
            
            if "价值链" in content or "利润分配" in content:
                score += max_scores["value_chain"]
                strengths.append("有价值链分析")
            
            if "退出" in content or "IPO" in content:
                score += max_scores["exit_path"]
            
            if "适合" in content and ("VC" in content or "PE" in content):
                score += max_scores["investor_type_fit"]
        
        # 写作质量评估
        elif dimension == ScoreDimension.WRITING_QUALITY:
            # 简单评估
            if len(content) > 5000:
                score += max_scores["logic_flow"]
            
            professional_terms = ["CAGR", "ROE", "PE", "估值", "毛利率"]
            if sum(1 for t in professional_terms if t in content) >= 3:
                score += max_scores["professional_language"]
                strengths.append("使用专业术语")
            
            # 检查AI水文
            ai_slop_patterns = ["总之", "综上所述", "不言而喻"]
            if sum(1 for p in ai_slop_patterns if p in content) < 3:
                score += max_scores["no_ai_slop"]
            else:
                weaknesses.append("存在AI水文痕迹")
                improvements.append("减少套话，增加实质内容")
            
            if "建议" in content or "策略" in content:
                score += max_scores["actionable"]
        
        return DimensionScore(
            dimension=dimension,
            score=score,
            weight=config["weight"],
            strengths=strengths,
            weaknesses=weaknesses,
            improvements=improvements
        )
    
    def _identify_critical_gaps(self, content: str) -> List[str]:
        """识别关键缺失"""
        gaps = []
        
        # 检查标的深拆
        if "收入结构" not in content and "业务板块" not in content:
            gaps.append("缺少标的深拆案例（必须添加1-2个重点公司的深度分析）")
        
        # 检查估值框架
        if "IRR" not in content and "MOIC" not in content:
            gaps.append("缺少估值与回报框架（必须添加IRR/MOIC测算）")
        
        # 检查反共识
        if "我们认为" not in content or "市场" not in content:
            gaps.append("缺少反共识观点（必须添加1-2个差异化判断）")
        
        return gaps
    
    def _generate_enhancement_checklist(self, scorecard: ReportScoreCard) -> List[Dict]:
        """生成补强清单"""
        checklist = []
        
        for ds in scorecard.dimension_scores:
            if ds.score < 70:
                for improvement in ds.improvements[:2]:
                    checklist.append({
                        "priority": "高" if ds.score < 50 else "中",
                        "item": improvement,
                        "score_boost": 5 if ds.score < 50 else 3,
                        "effort": "中等"
                    })
        
        # 按优先级排序
        priority_order = {"高": 0, "中": 1, "低": 2}
        checklist.sort(key=lambda x: priority_order.get(x["priority"], 2))
        
        return checklist[:10]  # 最多返回10项


# 创建全局实例
pe_report_scorer = PEReportScorer()


# 补强清单模板
ENHANCEMENT_CHECKLIST_TEMPLATE = """
# PE级行业研报补强清单

## 从L3到L4的关键升级（差2-3个模块）

### ✅ 模块1：标的深拆案例（必须）

**要求**：选择1-2个重点公司，进行"拆到骨头里"的分析

**内容清单**：
- [ ] 收入结构拆解（按业务板块）
- [ ] AI相关收入占比
- [ ] 毛利率分析（按业务板块）
- [ ] 财务指标对比（近3年）
- [ ] 杜邦分析
- [ ] 竞争对比（量化）
- [ ] 估值分析（历史分位）

**示例格式**：
```
## 海康威视深度分析

### 收入结构
| 业务板块 | 收入(亿) | 占比 | 增速 | 毛利率 | AI相关 |
|----------|----------|------|------|--------|--------|
| 国内主业 | 520 | 62% | +8% | 44% | 35% |
| 海外主业 | 210 | 25% | +12% | 42% | 30% |
| 创新业务 | 102 | 12% | +28% | 38% | 80% |

AI相关收入合计：约280亿，占比29%
```

---

### ✅ 模块2：估值与回报框架（必须）

**要求**：提供"财务投资语言"，不只是战略判断

**内容清单**：
- [ ] 估值锚点（至少2种方法）
- [ ] 可比公司估值对比
- [ ] 回报情景分析（乐观/中性/悲观）
- [ ] IRR/MOIC计算
- [ ] 赔率判断（上行空间 vs 下行风险）
- [ ] 投资者适配建议

**示例格式**：
```
## 估值与回报分析

### 估值锚点
| 方法 | 倍数 | 基础指标 | 隐含估值 |
|------|------|----------|----------|
| PE估值 | 22x | 净利润150亿 | 3300亿 |
| PS估值 | 3.5x | 营收950亿 | 3325亿 |

### 回报情景
| 情景 | 概率 | 退出估值 | IRR | MOIC |
|------|------|----------|-----|------|
| 乐观 | 25% | 5000亿 | 35% | 2.5x |
| 中性 | 50% | 4000亿 | 25% | 2.0x |
| 悲观 | 25% | 2500亿 | 10% | 1.3x |

期望IRR：23%，期望MOIC：1.9x
```

---

### ✅ 模块3：反共识判断（必须）

**要求**：展现"有立场的投资人"视角

**内容清单**：
- [ ] 明确市场共识
- [ ] 提出我们的不同判断
- [ ] 给出论证逻辑
- [ ] 承认错误风险
- [ ] 说明投资含义

**示例格式**：
```
## 反共识观点

### 观点1：中游平台价值可能被高估

**市场共识**：
> AI中游平台具有高价值，值得高估值

**我们的观点**：
> 大模型崛起将压缩中游平台价值，中游可能成为"夹心层"

**论证**：
1. 大模型具备端到端能力，绕过中游
   - GPT-4等可直接完成原本需要中游平台的任务
   - 数据：大模型API调用量同比增长300%

2. 上下游挤压中游利润空间
   - 上游算力成本居高不下
   - 下游客户议价能力增强

**如果我们错了**：
- 大模型落地不及预期
- 垂直领域know-how仍需中游承载

**投资含义**：
- 谨慎投资纯中游平台公司
- 关注有上下游延伸能力的公司
```

---

## 快速提升清单

| 优先级 | 补强项 | 预期提升 | 工作量 |
|--------|--------|----------|--------|
| 🔴 高 | 添加1个标的深拆 | +8分 | 2小时 |
| 🔴 高 | 添加估值框架 | +6分 | 1小时 |
| 🔴 高 | 添加1个反共识观点 | +5分 | 1小时 |
| 🟡 中 | 数据来源标注 | +3分 | 30分钟 |
| 🟡 中 | 微观风险量化 | +3分 | 30分钟 |
| 🟢 低 | 监控KPI | +2分 | 20分钟 |

**预计总提升**：15-20分（从L3稳定进入L4）
"""


def get_enhancement_checklist() -> str:
    """获取补强清单"""
    return ENHANCEMENT_CHECKLIST_TEMPLATE
