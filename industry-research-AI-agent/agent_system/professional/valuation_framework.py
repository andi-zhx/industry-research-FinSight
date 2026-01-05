# agent_system/professional/valuation_framework.py
"""
估值与回报框架模块
解决差距三：缺少明确的估值与回报框架

核心理念：
- 不只是"投资方向"，而是"财务投资语言"
- 包含：估值锚点、回报区间、赔率判断
- 区分VC/PE/产业资本的不同视角
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class InvestorType(Enum):
    """投资者类型"""
    VC = "风险投资"
    PE = "私募股权"
    STRATEGIC = "产业资本"
    PUBLIC = "二级市场"


class InvestmentStage(Enum):
    """投资阶段"""
    SEED = "种子轮"
    ANGEL = "天使轮"
    PRE_A = "Pre-A轮"
    SERIES_A = "A轮"
    SERIES_B = "B轮"
    SERIES_C = "C轮"
    PRE_IPO = "Pre-IPO"
    IPO = "IPO"
    SECONDARY = "二级市场"


class ExitPath(Enum):
    """退出路径"""
    IPO = "IPO上市"
    MA = "并购退出"
    SECONDARY = "老股转让"
    BUYBACK = "回购"
    DIVIDEND = "分红"


@dataclass
class ValuationAnchor:
    """估值锚点"""
    method: str                 # 估值方法
    multiple_type: str          # 倍数类型（PE/PB/PS/EV-EBITDA等）
    multiple_value: float       # 倍数值
    base_metric: str            # 基础指标
    base_value: float           # 基础值
    implied_value: float        # 隐含估值
    source: str                 # 来源/依据
    confidence: float = 0.8     # 置信度
    
    def to_string(self) -> str:
        return f"{self.method}：{self.multiple_value:.1f}x {self.multiple_type} × {self.base_value:.1f} = {self.implied_value:.1f}亿元"


@dataclass
class ComparableCompany:
    """可比公司"""
    name: str
    market_cap: float           # 市值（亿元）
    pe: float                   # PE
    pb: float                   # PB
    ps: float                   # PS
    ev_ebitda: float            # EV/EBITDA
    revenue_growth: float       # 营收增速
    net_margin: float           # 净利率
    roe: float                  # ROE
    business_similarity: float  # 业务相似度 0-1


@dataclass
class ReturnScenario:
    """回报情景"""
    scenario_name: str          # 情景名称（乐观/中性/悲观）
    entry_valuation: float      # 进入估值（亿元）
    exit_valuation: float       # 退出估值（亿元）
    holding_period: int         # 持有期（年）
    exit_path: ExitPath         # 退出路径
    irr: float                  # IRR
    moic: float                 # MOIC（投资倍数）
    probability: float          # 概率
    key_assumptions: List[str]  # 关键假设
    
    def calculate_irr(self):
        """计算IRR"""
        if self.holding_period > 0 and self.entry_valuation > 0:
            self.moic = self.exit_valuation / self.entry_valuation
            self.irr = (pow(self.moic, 1 / self.holding_period) - 1) * 100
    
    def to_string(self) -> str:
        return f"{self.scenario_name}：IRR {self.irr:.1f}%，MOIC {self.moic:.1f}x（{self.holding_period}年，{self.exit_path.value}）"


@dataclass
class InvestmentReturn:
    """投资回报分析"""
    target_name: str
    investor_type: InvestorType
    investment_stage: InvestmentStage
    
    # 估值锚点
    valuation_anchors: List[ValuationAnchor] = field(default_factory=list)
    
    # 可比公司
    comparable_companies: List[ComparableCompany] = field(default_factory=list)
    
    # 回报情景
    return_scenarios: List[ReturnScenario] = field(default_factory=list)
    
    # 综合估值
    target_valuation_low: float = 0
    target_valuation_mid: float = 0
    target_valuation_high: float = 0
    
    # 风险调整
    risk_discount: float = 0    # 风险折价
    liquidity_discount: float = 0  # 流动性折价
    
    def calculate_weighted_valuation(self) -> float:
        """计算加权估值"""
        if not self.valuation_anchors:
            return 0
        
        total_weight = sum(va.confidence for va in self.valuation_anchors)
        weighted_value = sum(va.implied_value * va.confidence for va in self.valuation_anchors)
        
        return weighted_value / total_weight if total_weight > 0 else 0
    
    def calculate_expected_return(self) -> Dict:
        """计算期望回报"""
        if not self.return_scenarios:
            return {}
        
        expected_irr = sum(s.irr * s.probability for s in self.return_scenarios)
        expected_moic = sum(s.moic * s.probability for s in self.return_scenarios)
        
        return {
            "expected_irr": expected_irr,
            "expected_moic": expected_moic,
            "best_case_irr": max(s.irr for s in self.return_scenarios),
            "worst_case_irr": min(s.irr for s in self.return_scenarios)
        }
    
    def generate_report(self) -> str:
        """生成估值与回报报告"""
        report = f"# {self.target_name} 估值与回报分析\n\n"
        report += f"**投资者类型**：{self.investor_type.value}\n"
        report += f"**投资阶段**：{self.investment_stage.value}\n\n"
        
        # 估值锚点
        report += "## 一、估值锚点\n\n"
        report += "| 估值方法 | 倍数 | 基础指标 | 隐含估值 | 置信度 |\n"
        report += "|----------|------|----------|----------|--------|\n"
        
        for va in self.valuation_anchors:
            report += f"| {va.method} | {va.multiple_value:.1f}x {va.multiple_type} | "
            report += f"{va.base_metric}={va.base_value:.1f} | {va.implied_value:.1f}亿 | {va.confidence:.0%} |\n"
        
        weighted_val = self.calculate_weighted_valuation()
        report += f"\n**加权估值**：{weighted_val:.1f}亿元\n\n"
        
        # 可比公司
        if self.comparable_companies:
            report += "## 二、可比公司估值\n\n"
            report += "| 公司 | 市值(亿) | PE | PB | PS | 营收增速 | 相似度 |\n"
            report += "|------|----------|-----|-----|-----|----------|--------|\n"
            
            for cc in self.comparable_companies:
                report += f"| {cc.name} | {cc.market_cap:.0f} | {cc.pe:.1f}x | {cc.pb:.1f}x | "
                report += f"{cc.ps:.1f}x | {cc.revenue_growth:.1f}% | {cc.business_similarity:.0%} |\n"
            
            # 计算可比公司均值
            avg_pe = sum(cc.pe * cc.business_similarity for cc in self.comparable_companies) / \
                     sum(cc.business_similarity for cc in self.comparable_companies)
            report += f"\n**可比公司加权PE均值**：{avg_pe:.1f}x\n\n"
        
        # 回报情景
        report += "## 三、回报情景分析\n\n"
        report += "| 情景 | 进入估值 | 退出估值 | 持有期 | IRR | MOIC | 概率 |\n"
        report += "|------|----------|----------|--------|-----|------|------|\n"
        
        for rs in self.return_scenarios:
            report += f"| {rs.scenario_name} | {rs.entry_valuation:.0f}亿 | {rs.exit_valuation:.0f}亿 | "
            report += f"{rs.holding_period}年 | {rs.irr:.1f}% | {rs.moic:.1f}x | {rs.probability:.0%} |\n"
        
        # 期望回报
        expected = self.calculate_expected_return()
        if expected:
            report += f"\n**期望IRR**：{expected['expected_irr']:.1f}%\n"
            report += f"**期望MOIC**：{expected['expected_moic']:.1f}x\n"
            report += f"**IRR区间**：{expected['worst_case_irr']:.1f}% ~ {expected['best_case_irr']:.1f}%\n\n"
        
        # 关键假设
        report += "## 四、关键假设\n\n"
        for rs in self.return_scenarios:
            report += f"### {rs.scenario_name}\n"
            for assumption in rs.key_assumptions:
                report += f"- {assumption}\n"
            report += "\n"
        
        return report


class ValuationFramework:
    """
    估值框架
    
    支持多种估值方法：
    1. 相对估值（PE/PB/PS/EV-EBITDA）
    2. DCF估值
    3. 可比公司估值
    4. 可比交易估值
    """
    
    # 行业估值参考
    INDUSTRY_VALUATION_BENCHMARKS = {
        "人工智能": {
            "pe_range": (30, 80),
            "ps_range": (5, 15),
            "growth_premium": 1.5,  # 高增长溢价
            "typical_exit_multiple": 25  # 典型退出倍数
        },
        "智能安防": {
            "pe_range": (15, 35),
            "ps_range": (2, 5),
            "growth_premium": 1.2,
            "typical_exit_multiple": 20
        },
        "金融科技": {
            "pe_range": (20, 50),
            "ps_range": (3, 10),
            "growth_premium": 1.3,
            "typical_exit_multiple": 22
        },
        "SaaS": {
            "pe_range": (40, 100),
            "ps_range": (8, 20),
            "growth_premium": 2.0,
            "typical_exit_multiple": 30
        },
        "半导体": {
            "pe_range": (25, 60),
            "ps_range": (4, 12),
            "growth_premium": 1.4,
            "typical_exit_multiple": 25
        }
    }
    
    # VC/PE投资回报基准
    RETURN_BENCHMARKS = {
        InvestmentStage.SEED: {"target_irr": 50, "target_moic": 10, "typical_holding": 7},
        InvestmentStage.ANGEL: {"target_irr": 45, "target_moic": 8, "typical_holding": 6},
        InvestmentStage.SERIES_A: {"target_irr": 40, "target_moic": 5, "typical_holding": 5},
        InvestmentStage.SERIES_B: {"target_irr": 35, "target_moic": 4, "typical_holding": 4},
        InvestmentStage.SERIES_C: {"target_irr": 30, "target_moic": 3, "typical_holding": 3},
        InvestmentStage.PRE_IPO: {"target_irr": 25, "target_moic": 2, "typical_holding": 2},
        InvestmentStage.SECONDARY: {"target_irr": 15, "target_moic": 1.5, "typical_holding": 3}
    }
    
    def __init__(self):
        pass
    
    def calculate_pe_valuation(
        self,
        net_profit: float,
        pe_multiple: float,
        growth_rate: float = 0,
        industry: str = ""
    ) -> ValuationAnchor:
        """PE估值"""
        
        # 如果有增长率，使用PEG调整
        if growth_rate > 0:
            peg = pe_multiple / growth_rate
            peg_comment = f"，PEG={peg:.1f}"
        else:
            peg_comment = ""
        
        implied_value = net_profit * pe_multiple
        
        return ValuationAnchor(
            method="PE估值",
            multiple_type="PE",
            multiple_value=pe_multiple,
            base_metric="净利润",
            base_value=net_profit,
            implied_value=implied_value,
            source=f"基于{industry}行业可比公司{peg_comment}",
            confidence=0.8
        )
    
    def calculate_ps_valuation(
        self,
        revenue: float,
        ps_multiple: float,
        industry: str = ""
    ) -> ValuationAnchor:
        """PS估值"""
        
        implied_value = revenue * ps_multiple
        
        return ValuationAnchor(
            method="PS估值",
            multiple_type="PS",
            multiple_value=ps_multiple,
            base_metric="营收",
            base_value=revenue,
            implied_value=implied_value,
            source=f"基于{industry}行业可比公司",
            confidence=0.7
        )
    
    def calculate_dcf_valuation(
        self,
        fcf_forecast: List[float],
        terminal_growth: float,
        wacc: float,
        terminal_multiple: float = 0
    ) -> ValuationAnchor:
        """DCF估值"""
        
        # 计算现值
        pv_fcf = 0
        for i, fcf in enumerate(fcf_forecast):
            pv_fcf += fcf / pow(1 + wacc, i + 1)
        
        # 终值
        if terminal_multiple > 0:
            # 使用退出倍数
            terminal_value = fcf_forecast[-1] * terminal_multiple
        else:
            # 使用永续增长
            terminal_value = fcf_forecast[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
        
        pv_terminal = terminal_value / pow(1 + wacc, len(fcf_forecast))
        
        implied_value = pv_fcf + pv_terminal
        
        return ValuationAnchor(
            method="DCF估值",
            multiple_type="DCF",
            multiple_value=0,
            base_metric="自由现金流",
            base_value=sum(fcf_forecast),
            implied_value=implied_value,
            source=f"WACC={wacc:.1%}，永续增长率={terminal_growth:.1%}",
            confidence=0.6
        )
    
    def calculate_comparable_valuation(
        self,
        target_metric: float,
        metric_type: str,
        comparable_companies: List[ComparableCompany]
    ) -> ValuationAnchor:
        """可比公司估值"""
        
        # 加权平均（按业务相似度）
        total_weight = sum(cc.business_similarity for cc in comparable_companies)
        
        if metric_type == "PE":
            weighted_multiple = sum(cc.pe * cc.business_similarity for cc in comparable_companies) / total_weight
        elif metric_type == "PB":
            weighted_multiple = sum(cc.pb * cc.business_similarity for cc in comparable_companies) / total_weight
        elif metric_type == "PS":
            weighted_multiple = sum(cc.ps * cc.business_similarity for cc in comparable_companies) / total_weight
        else:
            weighted_multiple = 0
        
        implied_value = target_metric * weighted_multiple
        
        return ValuationAnchor(
            method="可比公司估值",
            multiple_type=metric_type,
            multiple_value=weighted_multiple,
            base_metric="目标指标",
            base_value=target_metric,
            implied_value=implied_value,
            source=f"基于{len(comparable_companies)}家可比公司加权",
            confidence=0.75
        )
    
    def create_return_scenarios(
        self,
        entry_valuation: float,
        investment_stage: InvestmentStage,
        industry: str,
        revenue_growth_rate: float
    ) -> List[ReturnScenario]:
        """创建回报情景"""
        
        benchmark = self.RETURN_BENCHMARKS.get(investment_stage, {})
        industry_bench = self.INDUSTRY_VALUATION_BENCHMARKS.get(industry, {})
        
        typical_holding = benchmark.get("typical_holding", 5)
        exit_multiple = industry_bench.get("typical_exit_multiple", 20)
        
        scenarios = []
        
        # 乐观情景
        optimistic_growth = revenue_growth_rate * 1.3
        optimistic_exit = entry_valuation * pow(1 + optimistic_growth / 100, typical_holding) * 1.2
        optimistic = ReturnScenario(
            scenario_name="乐观",
            entry_valuation=entry_valuation,
            exit_valuation=optimistic_exit,
            holding_period=typical_holding,
            exit_path=ExitPath.IPO,
            irr=0, moic=0,
            probability=0.25,
            key_assumptions=[
                f"营收CAGR达到{optimistic_growth:.0f}%",
                "成功IPO，估值溢价20%",
                f"退出PE倍数{exit_multiple * 1.2:.0f}x"
            ]
        )
        optimistic.calculate_irr()
        scenarios.append(optimistic)
        
        # 中性情景
        neutral_growth = revenue_growth_rate
        neutral_exit = entry_valuation * pow(1 + neutral_growth / 100, typical_holding)
        neutral = ReturnScenario(
            scenario_name="中性",
            entry_valuation=entry_valuation,
            exit_valuation=neutral_exit,
            holding_period=typical_holding,
            exit_path=ExitPath.IPO,
            irr=0, moic=0,
            probability=0.50,
            key_assumptions=[
                f"营收CAGR维持{neutral_growth:.0f}%",
                "正常IPO退出",
                f"退出PE倍数{exit_multiple:.0f}x"
            ]
        )
        neutral.calculate_irr()
        scenarios.append(neutral)
        
        # 悲观情景
        pessimistic_growth = revenue_growth_rate * 0.5
        pessimistic_exit = entry_valuation * pow(1 + pessimistic_growth / 100, typical_holding) * 0.7
        pessimistic = ReturnScenario(
            scenario_name="悲观",
            entry_valuation=entry_valuation,
            exit_valuation=pessimistic_exit,
            holding_period=typical_holding + 1,
            exit_path=ExitPath.MA,
            irr=0, moic=0,
            probability=0.25,
            key_assumptions=[
                f"营收CAGR降至{pessimistic_growth:.0f}%",
                "并购退出，估值折价30%",
                f"退出PE倍数{exit_multiple * 0.7:.0f}x"
            ]
        )
        pessimistic.calculate_irr()
        scenarios.append(pessimistic)
        
        return scenarios
    
    def generate_investment_memo(
        self,
        target_name: str,
        investor_type: InvestorType,
        investment_stage: InvestmentStage,
        industry: str,
        financials: Dict,
        comparable_companies: List[ComparableCompany]
    ) -> InvestmentReturn:
        """生成投资备忘录"""
        
        investment = InvestmentReturn(
            target_name=target_name,
            investor_type=investor_type,
            investment_stage=investment_stage,
            comparable_companies=comparable_companies
        )
        
        # 计算多种估值
        net_profit = financials.get("net_profit", 0)
        revenue = financials.get("revenue", 0)
        growth_rate = financials.get("growth_rate", 20)
        
        if net_profit > 0:
            pe_val = self.calculate_pe_valuation(net_profit, 25, growth_rate, industry)
            investment.valuation_anchors.append(pe_val)
        
        if revenue > 0:
            ps_val = self.calculate_ps_valuation(revenue, 5, industry)
            investment.valuation_anchors.append(ps_val)
        
        if comparable_companies:
            comp_val = self.calculate_comparable_valuation(
                net_profit if net_profit > 0 else revenue,
                "PE" if net_profit > 0 else "PS",
                comparable_companies
            )
            investment.valuation_anchors.append(comp_val)
        
        # 计算回报情景
        entry_val = investment.calculate_weighted_valuation()
        if entry_val > 0:
            investment.return_scenarios = self.create_return_scenarios(
                entry_val, investment_stage, industry, growth_rate
            )
        
        return investment


# 创建全局实例
valuation_framework = ValuationFramework()


# Prompt模板：估值与回报分析
VALUATION_RETURN_PROMPT = """
【估值与回报分析要求】

你正在进行专业级投资分析，需要提供"财务投资语言"：

## 一、估值锚点（必须）

必须使用多种方法交叉验证：

### 1.1 相对估值
| 方法 | 倍数 | 基础指标 | 隐含估值 | 依据 |
|------|------|----------|----------|------|
| PE估值 | XXx | 净利润XX亿 | XX亿 | 可比公司均值 |
| PS估值 | XXx | 营收XX亿 | XX亿 | 行业惯例 |
| PB估值 | XXx | 净资产XX亿 | XX亿 | 历史中枢 |

### 1.2 DCF估值（如适用）
- WACC假设
- 永续增长率假设
- 终值计算方法

### 1.3 可比公司估值
| 公司 | 市值 | PE | PB | PS | 业务相似度 |
|------|------|-----|-----|-----|------------|

## 二、回报区间分析（必须）

### 2.1 情景分析
| 情景 | 概率 | 进入估值 | 退出估值 | 持有期 | IRR | MOIC |
|------|------|----------|----------|--------|-----|------|
| 乐观 | 25% | | | | | |
| 中性 | 50% | | | | | |
| 悲观 | 25% | | | | | |

### 2.2 期望回报
- 期望IRR：XX%
- 期望MOIC：XXx
- IRR区间：XX% ~ XX%

### 2.3 关键假设
每个情景的关键假设必须明确列出

## 三、赔率判断（必须）

### 3.1 上行空间 vs 下行风险
- 上行空间：XX%（乐观情景 vs 当前）
- 下行风险：XX%（悲观情景 vs 当前）
- 赔率：XX:1

### 3.2 风险调整后回报
- 风险折价：XX%
- 流动性折价：XX%（如适用）
- 调整后估值：XX亿

## 四、投资者适配（必须）

| 投资者类型 | 适合程度 | 理由 |
|------------|----------|------|
| VC | 高/中/低 | |
| PE | 高/中/低 | |
| 产业资本 | 高/中/低 | |
| 二级市场 | 高/中/低 | |

## 五、退出路径分析

| 退出方式 | 可能性 | 预期时间 | 预期倍数 |
|----------|--------|----------|----------|
| IPO | | | |
| 并购 | | | |
| 老股转让 | | | |

---

**VC/PE投资回报基准参考**：
| 阶段 | 目标IRR | 目标MOIC | 典型持有期 |
|------|---------|----------|------------|
| 种子轮 | 50%+ | 10x+ | 7年 |
| A轮 | 40%+ | 5x+ | 5年 |
| B轮 | 35%+ | 4x+ | 4年 |
| C轮 | 30%+ | 3x+ | 3年 |
| Pre-IPO | 25%+ | 2x+ | 2年 |
"""


def get_valuation_prompt(target_name: str, industry: str, stage: str) -> str:
    """获取估值分析Prompt"""
    return f"""
{VALUATION_RETURN_PROMPT}

【本次分析任务】
- 标的名称：{target_name}
- 所属行业：{industry}
- 投资阶段：{stage}

请按照上述框架进行估值与回报分析，确保：
1. 使用至少2种估值方法交叉验证
2. 提供3种情景的IRR/MOIC
3. 明确赔率判断
4. 给出投资者适配建议
"""
