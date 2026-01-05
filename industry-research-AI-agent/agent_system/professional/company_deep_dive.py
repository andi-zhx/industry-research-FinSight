# agent_system/professional/company_deep_dive.py
"""
标的深拆模块
解决差距二：缺少可直接投标的"深拆案例"

核心理念：
- 不只是"点名+定性判断"
- 而是"拆到骨头里"的公司分析
- 包含：财务拆解、收入结构、毛利来源、业务占比、竞争对比
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class BusinessSegment(Enum):
    """业务板块类型"""
    CORE = "核心业务"
    GROWTH = "成长业务"
    EMERGING = "新兴业务"
    LEGACY = "传统业务"


@dataclass
class RevenueBreakdown:
    """收入结构拆解"""
    segment_name: str           # 业务板块名称
    revenue: float              # 收入（亿元）
    revenue_pct: float          # 收入占比
    growth_rate: float          # 增速
    gross_margin: float         # 毛利率
    segment_type: BusinessSegment  # 业务类型
    ai_related: bool = False    # 是否AI相关
    ai_revenue_pct: float = 0   # AI相关收入占该板块比例
    key_products: List[str] = field(default_factory=list)  # 主要产品
    key_customers: List[str] = field(default_factory=list)  # 主要客户
    competitive_position: str = ""  # 竞争地位
    
    def get_ai_contribution(self) -> float:
        """计算AI贡献收入"""
        return self.revenue * self.ai_revenue_pct / 100 if self.ai_related else 0


@dataclass
class FinancialMetrics:
    """财务指标"""
    year: str
    revenue: float              # 营收（亿元）
    revenue_growth: float       # 营收增速
    gross_profit: float         # 毛利（亿元）
    gross_margin: float         # 毛利率
    operating_profit: float     # 营业利润（亿元）
    operating_margin: float     # 营业利润率
    net_profit: float           # 净利润（亿元）
    net_margin: float           # 净利率
    roe: float                  # ROE
    roa: float                  # ROA
    rd_expense: float           # 研发费用（亿元）
    rd_ratio: float             # 研发费用率
    capex: float = 0            # 资本开支（亿元）
    fcf: float = 0              # 自由现金流（亿元）
    
    def to_dict(self) -> Dict:
        return {
            "年份": self.year,
            "营收(亿元)": self.revenue,
            "营收增速": f"{self.revenue_growth:.1f}%",
            "毛利率": f"{self.gross_margin:.1f}%",
            "净利率": f"{self.net_margin:.1f}%",
            "ROE": f"{self.roe:.1f}%",
            "研发费用率": f"{self.rd_ratio:.1f}%"
        }


@dataclass
class CompetitiveComparison:
    """竞争对比"""
    metric_name: str
    company_value: float
    competitor_values: Dict[str, float]  # {竞争对手: 数值}
    industry_avg: float
    ranking: int
    comment: str = ""
    
    def get_vs_industry(self) -> str:
        """与行业平均对比"""
        diff = self.company_value - self.industry_avg
        if diff > 0:
            return f"高于行业平均 {abs(diff):.1f}"
        elif diff < 0:
            return f"低于行业平均 {abs(diff):.1f}"
        else:
            return "与行业平均持平"


@dataclass
class ValuationMetrics:
    """估值指标"""
    pe_ttm: float               # PE(TTM)
    pe_forward: float           # PE(Forward)
    pb: float                   # PB
    ps: float                   # PS
    ev_ebitda: float            # EV/EBITDA
    market_cap: float           # 市值（亿元）
    historical_pe_low: float    # 历史PE低点
    historical_pe_high: float   # 历史PE高点
    historical_pe_median: float # 历史PE中位数
    peer_pe_avg: float          # 可比公司PE均值
    
    def get_pe_percentile(self) -> float:
        """计算当前PE所处历史分位"""
        if self.historical_pe_high == self.historical_pe_low:
            return 50
        return (self.pe_ttm - self.historical_pe_low) / \
               (self.historical_pe_high - self.historical_pe_low) * 100
    
    def get_valuation_judgment(self) -> str:
        """估值判断"""
        percentile = self.get_pe_percentile()
        if percentile < 25:
            return "历史低位，具备安全边际"
        elif percentile < 50:
            return "历史中低位，估值合理"
        elif percentile < 75:
            return "历史中高位，估值偏高"
        else:
            return "历史高位，需警惕估值风险"


@dataclass
class CompanyDeepDive:
    """公司深度分析"""
    company_name: str
    stock_code: str
    industry: str
    sub_industry: str
    
    # 基本信息
    founded_year: int
    headquarters: str
    employees: int
    market_position: str  # 行业地位描述
    
    # 收入结构
    revenue_breakdown: List[RevenueBreakdown] = field(default_factory=list)
    
    # 财务数据（多年）
    financial_history: List[FinancialMetrics] = field(default_factory=list)
    
    # 竞争对比
    competitive_comparisons: List[CompetitiveComparison] = field(default_factory=list)
    
    # 估值
    valuation: Optional[ValuationMetrics] = None
    
    # AI相关分析
    ai_strategy: str = ""
    ai_products: List[str] = field(default_factory=list)
    ai_revenue_total: float = 0
    ai_revenue_pct: float = 0
    ai_growth_potential: str = ""
    
    # 核心竞争力
    competitive_advantages: List[str] = field(default_factory=list)
    competitive_risks: List[str] = field(default_factory=list)
    
    # 投资要点
    investment_highlights: List[str] = field(default_factory=list)
    investment_concerns: List[str] = field(default_factory=list)
    
    def calculate_ai_metrics(self):
        """计算AI相关指标"""
        total_revenue = sum(seg.revenue for seg in self.revenue_breakdown)
        ai_revenue = sum(seg.get_ai_contribution() for seg in self.revenue_breakdown)
        
        self.ai_revenue_total = ai_revenue
        self.ai_revenue_pct = (ai_revenue / total_revenue * 100) if total_revenue > 0 else 0
    
    def get_dupont_analysis(self) -> Dict:
        """杜邦分析"""
        if not self.financial_history:
            return {}
        
        latest = self.financial_history[-1]
        
        # ROE = 净利率 × 资产周转率 × 权益乘数
        # 简化计算（假设资产周转率和权益乘数）
        net_margin = latest.net_margin / 100
        
        return {
            "ROE": f"{latest.roe:.1f}%",
            "净利率": f"{latest.net_margin:.1f}%",
            "分析": f"ROE {latest.roe:.1f}% = 净利率 {latest.net_margin:.1f}% × 资产周转率 × 权益乘数"
        }
    
    def generate_deep_dive_report(self) -> str:
        """生成深度分析报告"""
        report = f"# {self.company_name}（{self.stock_code}）深度分析\n\n"
        
        # 一、公司概况
        report += "## 一、公司概况\n\n"
        report += f"- **行业地位**：{self.market_position}\n"
        report += f"- **成立时间**：{self.founded_year}年\n"
        report += f"- **总部**：{self.headquarters}\n"
        report += f"- **员工数**：{self.employees:,}人\n\n"
        
        # 二、收入结构拆解
        report += "## 二、收入结构拆解\n\n"
        report += "| 业务板块 | 收入(亿元) | 占比 | 增速 | 毛利率 | AI相关 |\n"
        report += "|----------|------------|------|------|--------|--------|\n"
        
        for seg in self.revenue_breakdown:
            ai_label = f"是({seg.ai_revenue_pct:.0f}%)" if seg.ai_related else "否"
            report += f"| {seg.segment_name} | {seg.revenue:.1f} | {seg.revenue_pct:.1f}% | "
            report += f"{seg.growth_rate:+.1f}% | {seg.gross_margin:.1f}% | {ai_label} |\n"
        
        # AI收入汇总
        self.calculate_ai_metrics()
        report += f"\n**AI相关收入合计**：{self.ai_revenue_total:.1f}亿元，占总收入{self.ai_revenue_pct:.1f}%\n\n"
        
        # 三、财务分析
        report += "## 三、财务分析\n\n"
        report += "### 3.1 核心财务指标\n\n"
        report += "| 年份 | 营收(亿元) | 增速 | 毛利率 | 净利率 | ROE | 研发费用率 |\n"
        report += "|------|------------|------|--------|--------|-----|------------|\n"
        
        for fm in self.financial_history:
            report += f"| {fm.year} | {fm.revenue:.1f} | {fm.revenue_growth:+.1f}% | "
            report += f"{fm.gross_margin:.1f}% | {fm.net_margin:.1f}% | "
            report += f"{fm.roe:.1f}% | {fm.rd_ratio:.1f}% |\n"
        
        # 杜邦分析
        dupont = self.get_dupont_analysis()
        if dupont:
            report += f"\n### 3.2 杜邦分析\n\n{dupont['分析']}\n\n"
        
        # 四、竞争对比
        if self.competitive_comparisons:
            report += "## 四、竞争对比\n\n"
            
            for comp in self.competitive_comparisons:
                report += f"### {comp.metric_name}\n\n"
                report += f"- **{self.company_name}**：{comp.company_value:.1f}\n"
                for competitor, value in comp.competitor_values.items():
                    report += f"- **{competitor}**：{value:.1f}\n"
                report += f"- **行业平均**：{comp.industry_avg:.1f}\n"
                report += f"- **排名**：第{comp.ranking}位\n"
                report += f"- **评价**：{comp.get_vs_industry()}\n\n"
        
        # 五、估值分析
        if self.valuation:
            report += "## 五、估值分析\n\n"
            report += "| 指标 | 当前值 | 历史低点 | 历史高点 | 可比均值 |\n"
            report += "|------|--------|----------|----------|----------|\n"
            report += f"| PE(TTM) | {self.valuation.pe_ttm:.1f}x | {self.valuation.historical_pe_low:.1f}x | "
            report += f"{self.valuation.historical_pe_high:.1f}x | {self.valuation.peer_pe_avg:.1f}x |\n"
            report += f"| PB | {self.valuation.pb:.1f}x | - | - | - |\n"
            report += f"| PS | {self.valuation.ps:.1f}x | - | - | - |\n"
            
            report += f"\n**估值分位**：当前PE处于历史{self.valuation.get_pe_percentile():.0f}%分位\n"
            report += f"**估值判断**：{self.valuation.get_valuation_judgment()}\n\n"
        
        # 六、AI战略分析
        report += "## 六、AI战略分析\n\n"
        report += f"### 6.1 AI战略定位\n\n{self.ai_strategy}\n\n"
        
        if self.ai_products:
            report += "### 6.2 AI产品/服务\n\n"
            for product in self.ai_products:
                report += f"- {product}\n"
            report += "\n"
        
        report += f"### 6.3 AI增长潜力\n\n{self.ai_growth_potential}\n\n"
        
        # 七、核心竞争力
        report += "## 七、核心竞争力分析\n\n"
        report += "### 7.1 竞争优势\n\n"
        for adv in self.competitive_advantages:
            report += f"- {adv}\n"
        
        report += "\n### 7.2 竞争风险\n\n"
        for risk in self.competitive_risks:
            report += f"- {risk}\n"
        
        # 八、投资要点
        report += "\n## 八、投资要点\n\n"
        report += "### 8.1 投资亮点\n\n"
        for highlight in self.investment_highlights:
            report += f"✅ {highlight}\n"
        
        report += "\n### 8.2 投资顾虑\n\n"
        for concern in self.investment_concerns:
            report += f"⚠️ {concern}\n"
        
        return report


class CompanyDeepDiveGenerator:
    """公司深度分析生成器"""
    
    def __init__(self):
        self.templates = {}
    
    def create_sample_deep_dive(self, company_name: str, stock_code: str) -> CompanyDeepDive:
        """创建示例深度分析（用于演示）"""
        
        # 示例：海康威视
        if "海康" in company_name:
            return self._create_hikvision_sample()
        
        # 通用模板
        return CompanyDeepDive(
            company_name=company_name,
            stock_code=stock_code,
            industry="",
            sub_industry="",
            founded_year=2000,
            headquarters="",
            employees=0,
            market_position=""
        )
    
    def _create_hikvision_sample(self) -> CompanyDeepDive:
        """创建海康威视示例分析"""
        
        deep_dive = CompanyDeepDive(
            company_name="海康威视",
            stock_code="002415.SZ",
            industry="人工智能",
            sub_industry="智能安防",
            founded_year=2001,
            headquarters="浙江杭州",
            employees=57000,
            market_position="全球安防行业龙头，连续多年全球市占率第一"
        )
        
        # 收入结构
        deep_dive.revenue_breakdown = [
            RevenueBreakdown(
                segment_name="国内主业（PBG+EBG+SMBG）",
                revenue=520,
                revenue_pct=62.5,
                growth_rate=8.5,
                gross_margin=44.2,
                segment_type=BusinessSegment.CORE,
                ai_related=True,
                ai_revenue_pct=35,
                key_products=["智能摄像机", "NVR", "视频云平台"],
                key_customers=["政府", "企业", "中小商户"],
                competitive_position="国内市占率约40%，绝对龙头"
            ),
            RevenueBreakdown(
                segment_name="海外主业",
                revenue=210,
                revenue_pct=25.3,
                growth_rate=12.3,
                gross_margin=42.5,
                segment_type=BusinessSegment.GROWTH,
                ai_related=True,
                ai_revenue_pct=30,
                key_products=["智能安防解决方案"],
                key_customers=["海外政企客户"],
                competitive_position="全球市占率约25%"
            ),
            RevenueBreakdown(
                segment_name="创新业务",
                revenue=102,
                revenue_pct=12.2,
                growth_rate=28.5,
                gross_margin=38.0,
                segment_type=BusinessSegment.EMERGING,
                ai_related=True,
                ai_revenue_pct=80,
                key_products=["萤石智能家居", "机器人", "汽车电子", "存储"],
                key_customers=["C端消费者", "汽车厂商"],
                competitive_position="多赛道布局，萤石已分拆上市"
            )
        ]
        
        # 财务历史
        deep_dive.financial_history = [
            FinancialMetrics(
                year="2021", revenue=814, revenue_growth=28.2,
                gross_profit=374, gross_margin=45.9,
                operating_profit=183, operating_margin=22.5,
                net_profit=168, net_margin=20.6,
                roe=28.5, roa=15.2,
                rd_expense=82, rd_ratio=10.1
            ),
            FinancialMetrics(
                year="2022", revenue=831, revenue_growth=2.1,
                gross_profit=369, gross_margin=44.4,
                operating_profit=165, operating_margin=19.9,
                net_profit=128, net_margin=15.4,
                roe=19.8, roa=10.5,
                rd_expense=93, rd_ratio=11.2
            ),
            FinancialMetrics(
                year="2023", revenue=893, revenue_growth=7.5,
                gross_profit=398, gross_margin=44.6,
                operating_profit=178, operating_margin=19.9,
                net_profit=141, net_margin=15.8,
                roe=20.2, roa=10.8,
                rd_expense=105, rd_ratio=11.8
            ),
            FinancialMetrics(
                year="2024E", revenue=958, revenue_growth=7.3,
                gross_profit=426, gross_margin=44.5,
                operating_profit=192, operating_margin=20.0,
                net_profit=153, net_margin=16.0,
                roe=20.5, roa=11.0,
                rd_expense=115, rd_ratio=12.0
            )
        ]
        
        # 竞争对比
        deep_dive.competitive_comparisons = [
            CompetitiveComparison(
                metric_name="毛利率",
                company_value=44.6,
                competitor_values={"大华股份": 38.5, "宇视科技": 35.2},
                industry_avg=40.0,
                ranking=1,
                comment="毛利率领先主要得益于品牌溢价和规模效应"
            ),
            CompetitiveComparison(
                metric_name="研发费用率",
                company_value=11.8,
                competitor_values={"大华股份": 12.5, "宇视科技": 10.8},
                industry_avg=11.0,
                ranking=2,
                comment="研发投入保持高位，AI算法持续迭代"
            ),
            CompetitiveComparison(
                metric_name="国内市占率",
                company_value=40.0,
                competitor_values={"大华股份": 25.0, "宇视科技": 10.0},
                industry_avg=15.0,
                ranking=1,
                comment="CR2达65%，双寡头格局稳固"
            )
        ]
        
        # 估值
        deep_dive.valuation = ValuationMetrics(
            pe_ttm=22.5,
            pe_forward=19.8,
            pb=3.8,
            ps=2.8,
            ev_ebitda=14.5,
            market_cap=2800,
            historical_pe_low=15.0,
            historical_pe_high=45.0,
            historical_pe_median=25.0,
            peer_pe_avg=20.0
        )
        
        # AI战略
        deep_dive.ai_strategy = """
海康威视AI战略定位为"AI赋能安防，安防拓展边界"：

1. **AI+安防**：将AI算法深度集成到摄像机、NVR等硬件产品，实现边缘智能
2. **AI开放平台**：推出AI开放平台，支持第三方算法部署，构建生态
3. **行业AI应用**：针对公安、交通、金融等行业开发专用AI解决方案
4. **大模型布局**：2024年发布"观澜"大模型，探索多模态AI应用
"""
        
        deep_dive.ai_products = [
            "智能摄像机系列（内置AI芯片，支持边缘计算）",
            "AI开放平台（支持算法训练、部署、管理）",
            "行业AI解决方案（智慧城市、智慧交通、智慧园区）",
            "观澜大模型（多模态理解、视频分析）"
        ]
        
        deep_dive.ai_growth_potential = """
**AI增长弹性分析**：

1. **短期（1-2年）**：AI渗透率提升带动ASP提升5-10%
2. **中期（3-5年）**：AI开放平台生态成熟，软件收入占比提升至20%+
3. **长期（5年+）**：大模型落地，开启新增长曲线

**AI收入预测**：
- 2024E：AI相关收入约280亿元，占比29%
- 2026E：AI相关收入约400亿元，占比35%
- CAGR：约20%
"""
        
        # 竞争优势
        deep_dive.competitive_advantages = [
            "品牌与渠道：全球最大安防品牌，渠道覆盖150+国家",
            "技术积累：20年+安防经验，AI算法业界领先",
            "规模效应：年出货量超1亿台，成本优势明显",
            "生态构建：AI开放平台聚集3000+开发者",
            "产品矩阵：从芯片到云端的全栈能力"
        ]
        
        deep_dive.competitive_risks = [
            "地缘政治：美国实体清单限制，海外业务承压",
            "竞争加剧：华为、阿里等科技巨头入局",
            "增长放缓：国内安防市场趋于成熟",
            "技术迭代：大模型可能重塑行业格局"
        ]
        
        # 投资要点
        deep_dive.investment_highlights = [
            "安防龙头地位稳固，国内CR1市占率约40%",
            "AI转型领先，AI相关收入占比近30%且快速增长",
            "创新业务多点开花，萤石、机器人、汽车电子均有突破",
            "估值处于历史中低位，PE约22x低于历史中枢25x",
            "现金流充沛，具备持续分红能力"
        ]
        
        deep_dive.investment_concerns = [
            "美国制裁风险：实体清单限制芯片采购和海外拓展",
            "增速放缓：国内安防市场增速降至个位数",
            "利润率承压：竞争加剧+研发投入增加",
            "大模型冲击：可能改变安防行业竞争格局"
        ]
        
        return deep_dive


# 创建全局实例
company_deep_dive_generator = CompanyDeepDiveGenerator()


# Prompt模板：标的深拆
COMPANY_DEEP_DIVE_PROMPT = """
【标的深拆分析要求】

你正在进行专业级公司研究，需要"拆到骨头里"的深度分析：

## 一、收入结构拆解（必须）

必须按业务板块拆解收入，每个板块包含：
- 收入金额和占比
- 增速
- 毛利率
- AI相关收入占比
- 主要产品/客户
- 竞争地位

**输出格式**：
| 业务板块 | 收入(亿元) | 占比 | 增速 | 毛利率 | AI相关 |
|----------|------------|------|------|--------|--------|
| 板块A | XX | XX% | XX% | XX% | 是/否(XX%) |

## 二、财务深度分析（必须）

### 2.1 核心财务指标（近3年+预测1年）
| 年份 | 营收 | 增速 | 毛利率 | 净利率 | ROE | 研发费用率 |
|------|------|------|--------|--------|-----|------------|

### 2.2 杜邦分析
ROE = 净利率 × 资产周转率 × 权益乘数
- 分析ROE的驱动因素
- 与历史和同业对比

### 2.3 现金流分析
- 经营现金流/净利润比率
- 自由现金流情况
- 资本开支计划

## 三、竞争对比分析（必须）

必须与主要竞争对手进行量化对比：

| 指标 | 本公司 | 竞争对手A | 竞争对手B | 行业平均 |
|------|--------|-----------|-----------|----------|
| 市占率 | | | | |
| 毛利率 | | | | |
| ROE | | | | |
| 研发费用率 | | | | |

## 四、估值分析（必须）

### 4.1 相对估值
| 指标 | 当前值 | 历史低点 | 历史高点 | 历史中位 | 可比均值 |
|------|--------|----------|----------|----------|----------|
| PE | | | | | |
| PB | | | | | |
| PS | | | | | |

### 4.2 估值判断
- 当前估值所处历史分位
- 与可比公司估值对比
- 估值是否合理的判断

## 五、AI相关分析（如适用）

### 5.1 AI战略定位
### 5.2 AI产品/服务
### 5.3 AI收入占比及增长
### 5.4 AI增长弹性测算

## 六、投资要点总结

### 6.1 核心竞争优势（3-5点）
### 6.2 主要风险因素（3-5点）
### 6.3 投资亮点（3点）
### 6.4 投资顾虑（3点）

---

**数据来源要求**：
- 财务数据必须来自上市公司年报/季报
- 市占率数据必须标注来源
- 估值数据必须标注日期
"""


def get_company_deep_dive_prompt(company_name: str, stock_code: str, industry: str) -> str:
    """获取公司深拆Prompt"""
    return f"""
{COMPANY_DEEP_DIVE_PROMPT}

【本次分析任务】
- 公司名称：{company_name}
- 股票代码：{stock_code}
- 所属行业：{industry}

请按照上述框架进行深度分析，确保：
1. 收入结构拆解到具体业务板块
2. 财务分析包含杜邦分析
3. 竞争对比有量化数据
4. 估值分析有历史分位判断
5. 所有数据标注来源
"""
