# agent_system/professional/__init__.py
"""
专业级研报模块
提供PE/VC级别的行业研究能力
"""

from .data_anchoring import (
    DataAnchoringFramework,
    data_anchoring_framework,
    get_data_anchoring_prompt,
    DATA_ANCHORING_PROMPT
)

from .company_deep_dive import (
    CompanyDeepDiveAnalyzer,
    company_deep_dive_analyzer,
    get_company_deep_dive_prompt,
    COMPANY_DEEP_DIVE_PROMPT
)

from .valuation_framework import (
    ValuationFramework,
    valuation_framework,
    get_valuation_prompt,
    VALUATION_PROMPT
)

from .micro_risk_analysis import (
    MicroRiskAnalyzer,
    micro_risk_analyzer,
    get_micro_risk_prompt,
    MICRO_RISK_PROMPT
)

from .contrarian_views import (
    ContrarianViewGenerator,
    contrarian_view_generator,
    get_contrarian_prompt,
    CONTRARIAN_VIEW_PROMPT
)

from .pe_report_scorer import (
    PEReportScorer,
    pe_report_scorer,
    get_enhancement_checklist,
    ENHANCEMENT_CHECKLIST_TEMPLATE
)

__all__ = [
    # 数据锚定
    "DataAnchoringFramework",
    "data_anchoring_framework",
    "get_data_anchoring_prompt",
    "DATA_ANCHORING_PROMPT",
    
    # 标的深拆
    "CompanyDeepDiveAnalyzer",
    "company_deep_dive_analyzer",
    "get_company_deep_dive_prompt",
    "COMPANY_DEEP_DIVE_PROMPT",
    
    # 估值框架
    "ValuationFramework",
    "valuation_framework",
    "get_valuation_prompt",
    "VALUATION_PROMPT",
    
    # 微观风险
    "MicroRiskAnalyzer",
    "micro_risk_analyzer",
    "get_micro_risk_prompt",
    "MICRO_RISK_PROMPT",
    
    # 反共识观点
    "ContrarianViewGenerator",
    "contrarian_view_generator",
    "get_contrarian_prompt",
    "CONTRARIAN_VIEW_PROMPT",
    
    # 研报评分
    "PEReportScorer",
    "pe_report_scorer",
    "get_enhancement_checklist",
    "ENHANCEMENT_CHECKLIST_TEMPLATE"
]
