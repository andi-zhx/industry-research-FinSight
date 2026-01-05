# FinSight 行研Agent V3.0 - PE级专业升级

## 升级概述

本次升级针对从L3（PE/产业资本内部研究）向L4（头部PE/一线券商首席级）跨越的5大结构性差距进行了全面补齐。

## 差距分析与解决方案

| 差距 | 问题描述 | 解决方案 | 新增模块 |
|------|----------|----------|----------|
| 差距一 | 数据可信度层级不够 | 锚定型数据框架 | `data_anchoring.py` |
| 差距二 | 缺少标的深拆案例 | 公司级深度分析 | `company_deep_dive.py` |
| 差距三 | 缺少估值与回报框架 | IRR/MOIC计算 | `valuation_framework.py` |
| 差距四 | 风险偏宏观 | 项目级微观风险 | `micro_risk_analysis.py` |
| 差距五 | 缺少反共识观点 | 差异化判断 | `contrarian_views.py` |

## 新增模块详解

### 1. 锚定型数据框架 (`data_anchoring.py`)

**核心理念**：从"推导型"数据升级为"锚定型"数据

**数据可信度分层**：
| 层级 | 来源 | 可信度 | 权重 |
|------|------|--------|------|
| Tier 1 | 统计局、央行、上市公司公告 | 最高 | 1.0 |
| Tier 2 | Wind、Bloomberg、头部券商 | 高 | 0.8 |
| Tier 3 | 艾瑞、IDC、行业协会 | 中等 | 0.6 |
| Tier 4 | 媒体报道、自行推算 | 低 | 0.3 |

**使用方法**：
```python
from agent_system.professional import data_anchoring_framework, get_data_anchoring_prompt

# 添加数据点
data_anchoring_framework.add_data_point(
    name="浙江省AI产业规模",
    value=3200,
    unit="亿元",
    source="浙江省统计局",
    tier=1
)

# 获取Prompt
prompt = get_data_anchoring_prompt("人工智能", "浙江省")
```

---

### 2. 标的深拆模块 (`company_deep_dive.py`)

**核心理念**："拆到骨头里"的公司分析

**分析框架**：
- 收入结构拆解（按业务板块）
- AI相关收入占比
- 财务深度分析（杜邦分析）
- 竞争对比（量化）
- 估值分析（历史分位）

**使用方法**：
```python
from agent_system.professional import company_deep_dive_analyzer, get_company_deep_dive_prompt

# 创建公司画像
profile = company_deep_dive_analyzer.create_company_profile(
    company_name="海康威视",
    stock_code="002415.SZ",
    industry="AI安防"
)

# 添加收入结构
profile.add_revenue_segment("国内主业", 520, 0.62, 0.08, 0.44, 0.35)
profile.add_revenue_segment("海外主业", 210, 0.25, 0.12, 0.42, 0.30)
profile.add_revenue_segment("创新业务", 102, 0.12, 0.28, 0.38, 0.80)

# 生成报告
report = profile.generate_deep_dive_report()
```

---

### 3. 估值与回报框架 (`valuation_framework.py`)

**核心理念**：提供"财务投资语言"

**估值方法**：
- PE估值（市盈率）
- PS估值（市销率）
- PB估值（市净率）
- DCF估值（现金流折现）
- EV/EBITDA估值

**回报分析**：
- 三种情景（乐观/中性/悲观）
- IRR计算
- MOIC计算
- 赔率分析（上行空间 vs 下行风险）

**使用方法**：
```python
from agent_system.professional import valuation_framework, get_valuation_prompt

# 创建估值分析
analysis = valuation_framework.create_valuation_analysis(
    company_name="海康威视",
    current_price=35.0,
    shares_outstanding=93.0
)

# 添加估值锚点
analysis.add_valuation_anchor("PE", 22, 150, "净利润")
analysis.add_valuation_anchor("PS", 3.5, 950, "营收")

# 添加回报情景
analysis.add_return_scenario("乐观", 0.25, 5000, 0.35, 2.5)
analysis.add_return_scenario("中性", 0.50, 4000, 0.25, 2.0)
analysis.add_return_scenario("悲观", 0.25, 2500, 0.10, 1.3)

# 生成报告
report = analysis.generate_valuation_report()
```

---

### 4. 微观风险分析 (`micro_risk_analysis.py`)

**核心理念**："投后视角的微观风险"

**产业链环节风险**：
| 环节 | 典型风险 | 量化指标 |
|------|----------|----------|
| 上游-芯片设计 | 流片失败、EDA受限 | 流片失败率30% |
| 上游-算力基础设施 | GPU供应受限 | 供应商集中度80% |
| 中游-AI平台 | 被云厂商替代 | 客户集中度50% |
| 下游-行业应用 | 项目制陷阱 | 项目转产品成功率30% |

**使用方法**：
```python
from agent_system.professional import micro_risk_analyzer, get_micro_risk_prompt

# 创建项目风险画像
profile = micro_risk_analyzer.create_project_risk_profile(
    project_name="XX公司",
    industry="人工智能",
    investment_stage="B轮",
    chain_segments=["中游-AI平台", "下游-行业应用"]
)

# 生成风险报告
report = profile.generate_risk_report()
```

---

### 5. 反共识观点模块 (`contrarian_views.py`)

**核心理念**："有立场的投资人"视角

**观点结构**：
1. 市场共识（XX%的市场参与者持此观点）
2. 我们的观点（与市场不同）
3. 核心论证（证据+数据）
4. 如果我们错了（风险）
5. 投资含义

**使用方法**：
```python
from agent_system.professional import contrarian_view_generator, get_contrarian_prompt

# 生成反共识章节
section = contrarian_view_generator.generate_contrarian_section(
    industry="人工智能",
    province="浙江省"
)

# 获取Prompt
prompt = get_contrarian_prompt("人工智能", "浙江省")
```

---

### 6. PE级研报评分器 (`pe_report_scorer.py`)

**评分维度**：
| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 数据可信度 | 25% | 一级来源占比、数据拆解、交叉验证 |
| 标的深拆 | 20% | 收入结构、财务分析、竞争对比 |
| 估值与回报 | 20% | 估值方法、情景分析、IRR/MOIC |
| 风险分析 | 15% | 微观风险、量化、监控指标 |
| 反共识观点 | 10% | 共识识别、论证、投资含义 |
| 投资导向 | 5% | TAM、价值链、退出路径 |
| 写作质量 | 5% | 逻辑、专业语言、可操作性 |

**等级划分**：
| 等级 | 分数 | 说明 |
|------|------|------|
| L4-顶级行研 | 85+ | 头部PE/一线券商首席级 |
| L3-专业行研 | 70-84 | 一线PE/产业资本内部研究 |
| L2-主流行研 | 55-69 | 主流券商行业分析师 |
| L1-基础行研 | <55 | 三四线券商/咨询公司 |

**使用方法**：
```python
from agent_system.professional import pe_report_scorer, get_enhancement_checklist

# 评分研报
scorecard = pe_report_scorer.score_report(report_content, "浙江省AI产业研究报告")

# 生成评分报告
report = scorecard.generate_scorecard_report()

# 获取补强清单
checklist = get_enhancement_checklist()
```

---

## 快速开始

### 1. 导入专业模块

```python
from agent_system.professional import (
    # 数据锚定
    data_anchoring_framework,
    get_data_anchoring_prompt,
    
    # 标的深拆
    company_deep_dive_analyzer,
    get_company_deep_dive_prompt,
    
    # 估值框架
    valuation_framework,
    get_valuation_prompt,
    
    # 微观风险
    micro_risk_analyzer,
    get_micro_risk_prompt,
    
    # 反共识观点
    contrarian_view_generator,
    get_contrarian_prompt,
    
    # 研报评分
    pe_report_scorer,
    get_enhancement_checklist
)
```

### 2. 生成PE级研报

```python
# 步骤1：数据收集（锚定型）
data_prompt = get_data_anchoring_prompt("人工智能", "浙江省")

# 步骤2：标的深拆
company_prompt = get_company_deep_dive_prompt("海康威视", "AI安防")

# 步骤3：估值分析
valuation_prompt = get_valuation_prompt("海康威视", "人工智能")

# 步骤4：风险分析
risk_prompt = get_micro_risk_prompt("XX项目", "人工智能", "中游-AI平台")

# 步骤5：反共识观点
contrarian_prompt = get_contrarian_prompt("人工智能", "浙江省")

# 步骤6：质量评估
scorecard = pe_report_scorer.score_report(final_report)
```

---

## 预期效果

| 指标 | V2.0 | V3.0 | 提升 |
|------|------|------|------|
| 数据可信度 | 60分 | 85分 | +25分 |
| 标的深拆 | 40分 | 80分 | +40分 |
| 估值框架 | 30分 | 85分 | +55分 |
| 风险分析 | 50分 | 80分 | +30分 |
| 反共识观点 | 20分 | 75分 | +55分 |
| **综合评分** | **L2-L3** | **L3-L4** | **+1级** |

---

## 文件结构

```
agent_system/professional/
├── __init__.py              # 模块导出
├── data_anchoring.py        # 锚定型数据框架
├── company_deep_dive.py     # 标的深拆模块
├── valuation_framework.py   # 估值与回报框架
├── micro_risk_analysis.py   # 微观风险分析
├── contrarian_views.py      # 反共识观点
└── pe_report_scorer.py      # PE级研报评分器
```

---

## 更新日志

- **V3.0** (2025-01-05): PE级专业升级，补齐5大结构性差距
- **V2.0** (2025-01-05): 架构升级，引入Agentic RAG和循环反馈
- **V1.0** (2025-01-04): 初始版本
