# agent_system/workflows/industry_research_v3.py
"""
行业研究工作流 V3.0 - PE级专业版
整合所有专业模块，生成投研级深度报告

核心升级（在V2.0基础上）：
1. 锚定型数据框架 - 数据可信度分层
2. 标的深拆 - 公司级深度分析
3. 估值与回报框架 - IRR/MOIC计算
4. 微观风险分析 - 项目级风险
5. 反共识观点 - 差异化判断
6. 研报评分 - 质量评估与补强
"""

import os
import re
import datetime
from typing import Dict, List, Optional, Any

# CrewAI核心
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# 基础Prompt
from agent_system.prompts.planner_prompt import get_planner_prompt
from agent_system.prompts.researcher_prompt import get_researcher_prompt
from agent_system.prompts.analyst_prompt import get_analyst_prompt
from agent_system.prompts.writer_prompt import get_writer_prompt
from agent_system.prompts.reviewer_prompt import get_reviewer_prompt

# V2.0增强模块
from agent_system.quality.data_quality import data_quality_checker, DataQualityRouter
from agent_system.context.global_context import global_context_manager, fact_checker
from agent_system.rag.agentic_rag import query_rewriter, chunk_reranker, self_reflective_rag
from agent_system.tools.enhanced_search import (
    financial_data_search,
    policy_search_enhanced,
    market_size_search_enhanced,
    competitive_analysis_search,
    supply_chain_search_enhanced,
    investment_search,
    code_executor_tool
)
from agent_system.postprocess.reviewer_parser import parse_reviewer_output

# V3.0 PE级专业模块
from agent_system.professional.data_anchoring import (
    data_anchoring_framework,
    get_data_anchoring_prompt,
    DATA_ANCHORING_PROMPT
)
from agent_system.professional.company_deep_dive import (
    company_deep_dive_analyzer,
    get_company_deep_dive_prompt,
    COMPANY_DEEP_DIVE_PROMPT
)
from agent_system.professional.valuation_framework import (
    valuation_framework,
    get_valuation_prompt,
    VALUATION_PROMPT
)
from agent_system.professional.micro_risk_analysis import (
    micro_risk_analyzer,
    get_micro_risk_prompt,
    MICRO_RISK_PROMPT
)
from agent_system.professional.contrarian_views import (
    contrarian_view_generator,
    get_contrarian_prompt,
    CONTRARIAN_VIEW_PROMPT
)
from agent_system.professional.pe_report_scorer import (
    pe_report_scorer,
    get_enhancement_checklist
)

# 记忆系统
try:
    from memory_system.enhanced_memory import enhanced_memory, fact_validation
except ImportError:
    enhanced_memory = None
    fact_validation = None

try:
    from memory_system.memory_manager import memory_manager
except ImportError:
    memory_manager = None


class IndustryResearchWorkflowV3:
    """
    行业研究工作流 V3.0 - PE级专业版
    生成符合头部PE/一线券商首席级标准的深度研报
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini", verbose: bool = True):
        """
        初始化工作流
        
        Args:
            model_name: LLM模型名称
            verbose: 是否输出详细日志
        """
        self.model_name = model_name
        self.verbose = verbose
        
        # 初始化基础搜索工具
        self.search_tool = SerperDevTool(n_results=10)
        
        # 增强搜索工具集
        self.enhanced_tools = [
            self.search_tool,
            financial_data_search,
            policy_search_enhanced,
            market_size_search_enhanced,
            competitive_analysis_search,
            supply_chain_search_enhanced,
            investment_search,
            code_executor_tool
        ]
        
        # 数据质量路由器
        self.quality_router = DataQualityRouter()
        
        # 研究状态
        self.state = {
            "iteration": 0,
            "max_iterations": 3,
            "data_coverage": 0.0,
            "quality_passed": False,
            "pe_score": 0.0
        }
        
        # 重点公司列表（用于标的深拆）
        self.key_companies = []
    
    def run(self, industry: str, province: str, target_year: str = "2025",
            focus: str = "综合分析", max_revisions: int = 2,
            key_companies: List[str] = None) -> Dict[str, Any]:
        """
        运行PE级行业研究工作流
        
        Args:
            industry: 行业名称
            province: 省份
            target_year: 目标年份
            focus: 研究侧重点
            max_revisions: 最大修订次数
            key_companies: 重点分析的公司列表
        
        Returns:
            Dict: 研究结果
        """
        print(f"\n{'='*70}")
        print(f"🚀 启动行业研究工作流 V3.0 - PE级专业版")
        print(f"   行业: {industry} | 区域: {province} | 年份: {target_year}")
        print(f"   侧重: {focus} | 最大修订: {max_revisions}次")
        if key_companies:
            print(f"   重点公司: {', '.join(key_companies)}")
        print(f"{'='*70}\n")
        
        self.key_companies = key_companies or []
        
        # 初始化全局上下文
        global_context_manager.init_context(industry, province, target_year, focus)
        
        # 初始化数据锚定框架
        data_anchoring_framework.clear()
        
        # 初始化增强记忆会话
        if enhanced_memory:
            enhanced_memory.start_session(industry, province, target_year, focus)
        
        # 设置查询改写器上下文
        query_rewriter.set_context(
            industry=industry,
            province=province,
            year=target_year
        )
        
        try:
            # Phase 1: 规划
            print("\n📋 Phase 1: 研究规划（PE级）")
            plan = self._phase_planning_pe(industry, province, target_year, focus)
            
            # Phase 2: 研究（锚定型数据）
            print("\n🔍 Phase 2: 数据研究（锚定型）")
            research_data = self._phase_research_anchored(
                industry, province, target_year, focus, plan
            )
            
            # Phase 3: 标的深拆
            print("\n🏢 Phase 3: 标的深拆")
            company_analysis = self._phase_company_deep_dive(
                industry, province, target_year, research_data
            )
            
            # Phase 4: 深度分析
            print("\n📊 Phase 4: 深度分析")
            analysis = self._phase_analysis_pe(
                industry, province, target_year, focus, research_data, company_analysis
            )
            
            # Phase 5: 估值与回报
            print("\n💰 Phase 5: 估值与回报分析")
            valuation_analysis = self._phase_valuation(
                industry, province, target_year, company_analysis
            )
            
            # Phase 6: 微观风险
            print("\n⚠️ Phase 6: 微观风险分析")
            risk_analysis = self._phase_micro_risk(
                industry, province, target_year
            )
            
            # Phase 7: 反共识观点
            print("\n💡 Phase 7: 反共识观点")
            contrarian_section = self._phase_contrarian_views(
                industry, province, target_year
            )
            
            # Phase 8: 报告撰写
            print("\n✍️ Phase 8: 报告撰写（PE级）")
            report = self._phase_writing_pe(
                industry, province, target_year, focus,
                research_data, company_analysis, analysis,
                valuation_analysis, risk_analysis, contrarian_section
            )
            
            # Phase 9: 审核与修订
            print("\n🔄 Phase 9: 审核与修订")
            final_report = self._phase_review_and_revise_pe(
                industry, province, target_year, focus,
                report, research_data, analysis, max_revisions
            )
            
            # Phase 10: PE级质量评估
            print("\n📈 Phase 10: PE级质量评估")
            scorecard = pe_report_scorer.score_report(final_report, f"{province}{industry}行业研究报告")
            self.state["pe_score"] = scorecard.overall_score
            
            print(f"   📊 PE级评分: {scorecard.overall_score:.1f}/100")
            print(f"   📊 研报等级: {scorecard.report_level.value}")
            
            # 如果评分不够，进行补强
            if scorecard.overall_score < 70 and self.state["iteration"] < self.state["max_iterations"]:
                print(f"   ⚠️ 评分不足70分，进行补强...")
                final_report = self._enhance_report(
                    final_report, scorecard, industry, province, target_year
                )
                # 重新评分
                scorecard = pe_report_scorer.score_report(final_report, f"{province}{industry}行业研究报告")
                self.state["pe_score"] = scorecard.overall_score
                print(f"   📊 补强后评分: {scorecard.overall_score:.1f}/100")
            
            # 结束会话
            quality_score = self.state.get("data_coverage", 0.8)
            if enhanced_memory:
                enhanced_memory.end_session(final_report, quality_score)
            
            # 保存报告
            output_path = self._save_report(final_report, industry, province, target_year)
            
            # 保存评分报告
            scorecard_path = self._save_scorecard(scorecard, industry, province, target_year)
            
            print(f"\n{'='*70}")
            print(f"✅ PE级研究完成!")
            print(f"   报告路径: {output_path}")
            print(f"   评分报告: {scorecard_path}")
            print(f"   数据覆盖率: {quality_score:.1%}")
            print(f"   PE级评分: {scorecard.overall_score:.1f}/100 ({scorecard.report_level.value})")
            print(f"{'='*70}\n")
            
            return {
                "success": True,
                "report": final_report,
                "output_path": output_path,
                "scorecard_path": scorecard_path,
                "quality_score": quality_score,
                "pe_score": scorecard.overall_score,
                "report_level": scorecard.report_level.value,
                "iterations": self.state["iteration"]
            }
        
        except Exception as e:
            print(f"\n❌ 研究过程出错: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "iterations": self.state["iteration"]
            }
    
    def _phase_planning_pe(self, industry: str, province: str, 
                           target_year: str, focus: str) -> str:
        """Phase 1: PE级研究规划"""
        
        # 获取历史研究建议
        suggestions = ""
        if memory_manager:
            try:
                context = memory_manager.get_industry_context(industry, province)
                if context:
                    suggestions = f"\n\n【历史研究经验】\n{context}"
            except:
                pass
        
        # PE级规划要求
        pe_planning_requirements = """
【PE级研究规划要求】

1. 数据收集规划（锚定型）
   - 明确需要的Tier 1数据（统计局、央行、上市公司公告）
   - 明确需要的Tier 2数据（Wind、Bloomberg、头部券商）
   - 识别可能需要推算的数据点

2. 标的深拆规划
   - 选择2-3家重点公司进行深度分析
   - 明确需要拆解的财务指标
   - 规划竞争对比维度

3. 估值框架规划
   - 确定适用的估值方法（PE/PS/DCF等）
   - 规划回报情景分析
   - 明确IRR/MOIC计算所需数据

4. 风险分析规划
   - 识别产业链环节特有风险
   - 规划微观风险量化指标
   - 设计监控KPI

5. 反共识观点规划
   - 识别市场主流观点
   - 规划差异化判断方向
"""
        
        planner = Agent(
            role="PE级研究规划师",
            goal=f"为{province}{industry}行业研究制定PE级专业研究计划",
            backstory=get_planner_prompt() + pe_planning_requirements,
            llm=self.model_name,
            verbose=self.verbose
        )
        
        planning_task = Task(
            description=f"""
请为以下研究项目制定PE级专业研究计划：

【研究主题】
- 行业：{industry}
- 区域：{province}
- 目标年份：{target_year}
- 研究侧重：{focus}
{suggestions}

{pe_planning_requirements}

【输出要求】
1. 研究目标和范围
2. 数据需求清单（按Tier分级）
3. 重点公司列表（2-3家）
4. 章节结构（包含标的深拆、估值、风险、反共识）
5. 时间和资源规划

请输出结构化的PE级研究计划。
""",
            expected_output="PE级研究计划，包含数据分级、标的选择、估值框架、风险维度",
            agent=planner
        )
        
        crew = Crew(
            agents=[planner],
            tasks=[planning_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        plan = str(result)
        
        # 从计划中提取重点公司
        self._extract_key_companies(plan, industry)
        
        print(f"   ✓ PE级研究计划已生成")
        if self.key_companies:
            print(f"   📌 重点公司: {', '.join(self.key_companies)}")
        
        return plan
    
    def _extract_key_companies(self, plan: str, industry: str):
        """从计划中提取重点公司"""
        # 简单的公司名称提取（可以根据实际情况优化）
        common_companies = {
            "人工智能": ["海康威视", "大华股份", "科大讯飞", "商汤科技", "旷视科技", "云从科技"],
            "新能源": ["宁德时代", "比亚迪", "隆基绿能", "阳光电源"],
            "半导体": ["中芯国际", "华虹半导体", "韦尔股份", "北方华创"],
            "医药": ["恒瑞医药", "药明康德", "迈瑞医疗", "爱尔眼科"]
        }
        
        # 如果用户没有指定，从计划中查找或使用默认
        if not self.key_companies:
            for company in common_companies.get(industry, []):
                if company in plan:
                    self.key_companies.append(company)
            
            # 如果还是没有，使用默认
            if not self.key_companies and industry in common_companies:
                self.key_companies = common_companies[industry][:2]
    
    def _phase_research_anchored(self, industry: str, province: str,
                                  target_year: str, focus: str, 
                                  plan: str) -> str:
        """Phase 2: 锚定型数据研究"""
        
        # 获取锚定型数据Prompt
        anchoring_prompt = get_data_anchoring_prompt(industry, province)
        
        researcher = Agent(
            role="PE级行业研究员",
            goal=f"收集{province}{industry}行业的锚定型数据",
            backstory=get_researcher_prompt() + "\n\n" + anchoring_prompt,
            tools=self.enhanced_tools,
            llm=self.model_name,
            verbose=self.verbose
        )
        
        context_prompt = global_context_manager.export_context_prompt()
        
        research_task = Task(
            description=f"""
根据研究计划，收集{province}{industry}行业的锚定型数据。

【研究计划】
{plan}

【全局上下文】
{context_prompt}

{DATA_ANCHORING_PROMPT}

【数据收集要求】
1. 优先使用Tier 1来源（统计局、央行、上市公司公告）
2. 每个数据点必须标注来源和可信度层级
3. 对于推算数据，必须说明推算方法
4. 进行数据交叉验证

【必须收集的数据】
1. 市场规模（总量、细分）
2. 增长率（CAGR、同比）
3. 产业链结构
4. 竞争格局（CR5、龙头份额）
5. 政策环境
6. 投融资数据

请确保每个数据点都标注来源和Tier级别。
""",
            expected_output="锚定型数据报告，每个数据标注来源和Tier级别",
            agent=researcher
        )
        
        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        research_data = str(result)
        
        # 数据质量检查
        quality = data_quality_checker.check_coverage(research_data)
        self.state["data_coverage"] = quality.total_score
        
        print(f"   ✓ 锚定型数据收集完成")
        print(f"   📊 数据覆盖率: {quality.total_score:.1%}")
        
        return research_data
    
    def _phase_company_deep_dive(self, industry: str, province: str,
                                  target_year: str, research_data: str) -> str:
        """Phase 3: 标的深拆"""
        
        if not self.key_companies:
            print(f"   ⚠️ 未指定重点公司，跳过标的深拆")
            return ""
        
        # 获取标的深拆Prompt
        company_prompt = get_company_deep_dive_prompt(
            self.key_companies[0] if self.key_companies else "龙头企业",
            industry
        )
        
        analyst = Agent(
            role="标的深拆分析师",
            goal=f"对{industry}行业重点公司进行深度拆解分析",
            backstory=company_prompt,
            tools=self.enhanced_tools,
            llm=self.model_name,
            verbose=self.verbose
        )
        
        companies_str = "、".join(self.key_companies)
        
        deep_dive_task = Task(
            description=f"""
对以下重点公司进行"拆到骨头里"的深度分析：

【重点公司】
{companies_str}

【行业背景】
{research_data[:3000]}

{COMPANY_DEEP_DIVE_PROMPT}

【分析要求】
对每家公司必须包含：
1. 收入结构拆解（按业务板块）
2. AI相关收入占比
3. 毛利率分析（按业务板块）
4. 财务指标对比（近3年）
5. 杜邦分析（ROE拆解）
6. 竞争对比（量化）
7. 估值分析（历史分位）

请输出详细的标的深拆报告。
""",
            expected_output="标的深拆报告，包含收入结构、财务分析、竞争对比",
            agent=analyst
        )
        
        crew = Crew(
            agents=[analyst],
            tasks=[deep_dive_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        company_analysis = str(result)
        
        print(f"   ✓ 标的深拆完成: {companies_str}")
        
        return company_analysis
    
    def _phase_analysis_pe(self, industry: str, province: str,
                           target_year: str, focus: str,
                           research_data: str, company_analysis: str) -> str:
        """Phase 4: PE级深度分析"""
        
        analyst = Agent(
            role="PE级行业分析师",
            goal=f"对{province}{industry}行业进行PE级深度分析",
            backstory=get_analyst_prompt(),
            tools=[code_executor_tool],
            llm=self.model_name,
            verbose=self.verbose
        )
        
        analysis_task = Task(
            description=f"""
基于收集的数据进行PE级深度分析：

【研究数据】
{research_data[:4000]}

【标的深拆】
{company_analysis[:3000]}

【分析框架】
1. 市场规模分析
   - TAM/SAM/SOM拆解
   - 增长驱动因素
   - 天花板测算

2. 竞争格局分析
   - 波特五力模型
   - 竞争壁垒评估
   - 龙头优势分析

3. 产业链分析
   - 价值链分配
   - 各环节利润率
   - 上下游议价能力

4. 投资价值分析
   - 行业生命周期定位
   - 投资时机判断
   - 适合的投资者类型

请使用Python代码执行器进行必要的计算（如CAGR、市场份额等）。
""",
            expected_output="PE级深度分析报告",
            agent=analyst
        )
        
        crew = Crew(
            agents=[analyst],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        analysis = str(result)
        
        print(f"   ✓ PE级深度分析完成")
        
        return analysis
    
    def _phase_valuation(self, industry: str, province: str,
                         target_year: str, company_analysis: str) -> str:
        """Phase 5: 估值与回报分析"""
        
        if not self.key_companies:
            return ""
        
        # 获取估值Prompt
        valuation_prompt = get_valuation_prompt(
            self.key_companies[0] if self.key_companies else "龙头企业",
            industry
        )
        
        analyst = Agent(
            role="估值分析师",
            goal=f"对{industry}行业重点公司进行估值与回报分析",
            backstory=valuation_prompt,
            tools=[code_executor_tool],
            llm=self.model_name,
            verbose=self.verbose
        )
        
        valuation_task = Task(
            description=f"""
对重点公司进行估值与回报分析：

【标的深拆】
{company_analysis[:4000]}

{VALUATION_PROMPT}

【分析要求】
1. 估值锚点（至少2种方法）
2. 可比公司估值对比
3. 回报情景分析（乐观/中性/悲观）
4. IRR/MOIC计算
5. 赔率判断
6. 投资者适配建议

请使用Python代码执行器计算IRR和MOIC。
""",
            expected_output="估值与回报分析报告，包含IRR/MOIC计算",
            agent=analyst
        )
        
        crew = Crew(
            agents=[analyst],
            tasks=[valuation_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        valuation_analysis = str(result)
        
        print(f"   ✓ 估值与回报分析完成")
        
        return valuation_analysis
    
    def _phase_micro_risk(self, industry: str, province: str,
                          target_year: str) -> str:
        """Phase 6: 微观风险分析"""
        
        # 获取微观风险Prompt
        risk_prompt = get_micro_risk_prompt(
            f"{province}{industry}投资项目",
            industry,
            "中游-AI平台"  # 默认，可根据实际调整
        )
        
        analyst = Agent(
            role="风险分析师",
            goal=f"对{province}{industry}行业进行项目级微观风险分析",
            backstory=risk_prompt,
            llm=self.model_name,
            verbose=self.verbose
        )
        
        risk_task = Task(
            description=f"""
对{province}{industry}行业进行项目级微观风险分析：

{MICRO_RISK_PROMPT}

【分析要求】
1. 产业链环节风险
   - 上游：流片失败率、供应商集中度
   - 中游：客户集中度、被替代风险
   - 下游：项目转产品成功率、续费率

2. 微观风险清单
   - 每个风险：概率、影响、趋势
   - 量化影响
   - 触发条件和预警信号

3. 风险矩阵

4. 监控建议
   - 关键KPI
   - 监控频率
   - 预警阈值

请输出详细的微观风险分析报告。
""",
            expected_output="微观风险分析报告，包含量化风险和监控建议",
            agent=analyst
        )
        
        crew = Crew(
            agents=[analyst],
            tasks=[risk_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        risk_analysis = str(result)
        
        print(f"   ✓ 微观风险分析完成")
        
        return risk_analysis
    
    def _phase_contrarian_views(self, industry: str, province: str,
                                 target_year: str) -> str:
        """Phase 7: 反共识观点"""
        
        # 获取反共识Prompt
        contrarian_prompt = get_contrarian_prompt(industry, province)
        
        analyst = Agent(
            role="策略分析师",
            goal=f"对{province}{industry}行业提出反共识观点",
            backstory=contrarian_prompt,
            llm=self.model_name,
            verbose=self.verbose
        )
        
        contrarian_task = Task(
            description=f"""
对{province}{industry}行业提出反共识观点：

{CONTRARIAN_VIEW_PROMPT}

【分析要求】
针对以下议题提出反共识判断：
1. 市场增速是否被高估/低估？
2. 龙头企业竞争优势是否可持续？
3. 当前估值水平是否合理？
4. 主流技术路线是否正确？
5. 政策红利是否被过度解读？

每个反共识观点必须：
- 明确市场共识
- 给出我们的判断
- 提供论证逻辑
- 承认错误风险
- 说明投资含义

请输出2-3个有价值的反共识观点。
""",
            expected_output="反共识观点章节，包含论证和投资含义",
            agent=analyst
        )
        
        crew = Crew(
            agents=[analyst],
            tasks=[contrarian_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        contrarian_section = str(result)
        
        print(f"   ✓ 反共识观点生成完成")
        
        return contrarian_section
    
    def _phase_writing_pe(self, industry: str, province: str,
                          target_year: str, focus: str,
                          research_data: str, company_analysis: str,
                          analysis: str, valuation_analysis: str,
                          risk_analysis: str, contrarian_section: str) -> str:
        """Phase 8: PE级报告撰写"""
        
        context_prompt = global_context_manager.export_context_prompt()
        
        writer = Agent(
            role="PE级研究报告撰写专家",
            goal=f"撰写{province}{industry}行业PE级深度研究报告",
            backstory=get_writer_prompt(),
            llm=self.model_name,
            verbose=self.verbose
        )
        
        writing_task = Task(
            description=f"""
整合所有分析内容，撰写PE级深度研究报告：

【研究数据】
{research_data[:3000]}

【标的深拆】
{company_analysis[:3000]}

【深度分析】
{analysis[:3000]}

【估值分析】
{valuation_analysis[:2000]}

【风险分析】
{risk_analysis[:2000]}

【反共识观点】
{contrarian_section[:2000]}

【全局上下文】
{context_prompt}

【PE级报告结构】
1. 摘要（核心观点、投资建议、目标公司）
2. 行业概述
3. 市场规模与增长（锚定型数据）
4. 产业链分析（价值链分配）
5. 竞争格局
6. **标的深拆**（重点公司深度分析）
7. **估值与回报**（IRR/MOIC）
8. 政策环境
9. **微观风险分析**（项目级风险）
10. **反共识观点**
11. 投资建议（分投资者类型）
12. 附录（数据来源、方法论）

【写作要求】
- 使用专业的PE投研语言
- 所有数据标注来源和Tier级别
- 确保数据与全局上下文一致
- 图表使用Markdown表格
- 字数要求：12000-15000字
- 避免AI水文，每句话都要有信息量

请输出完整的PE级研究报告。
""",
            expected_output="PE级深度研究报告，Markdown格式",
            agent=writer
        )
        
        crew = Crew(
            agents=[writer],
            tasks=[writing_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        report = str(result)
        
        print(f"   ✓ PE级报告撰写完成")
        
        return report
    
    def _phase_review_and_revise_pe(self, industry: str, province: str,
                                     target_year: str, focus: str,
                                     report: str, research_data: str,
                                     analysis: str, max_revisions: int) -> str:
        """Phase 9: PE级审核与修订"""
        
        current_report = report
        
        for revision in range(max_revisions):
            print(f"   📝 第 {revision + 1} 轮PE级审核...")
            
            # 事实核查
            if fact_validation:
                passed, corrected, issues = fact_validation.validate_before_write(
                    current_report, "Writer"
                )
                if not passed:
                    print(f"      ⚠️ 发现 {len(issues)} 个数据一致性问题")
                    current_report = corrected
            
            # PE级审核
            reviewer = Agent(
                role="PE级研究报告审核专家",
                goal="按照PE级标准审核研究报告",
                backstory=get_reviewer_prompt() + """

【PE级审核标准】
1. 数据可信度 - 是否使用锚定型数据，来源是否标注
2. 标的深拆 - 是否有公司级深度分析
3. 估值框架 - 是否有IRR/MOIC计算
4. 风险分析 - 是否有微观风险量化
5. 反共识观点 - 是否有差异化判断
""",
                llm=self.model_name,
                verbose=self.verbose
            )
            
            review_task = Task(
                description=f"""
请按照PE级标准审核以下研究报告：

【报告内容】
{current_report[:12000]}

【PE级审核要点】
1. 数据可信度 - 锚定型数据占比
2. 标的深拆 - 公司分析深度
3. 估值框架 - IRR/MOIC是否完整
4. 风险分析 - 微观风险是否量化
5. 反共识观点 - 是否有差异化判断
6. 写作质量 - 是否避免AI水文

【输出格式】
REVIEW_RESULT: PASS 或 NEED_REVISION
SCORE: XX/100
PE_LEVEL: L1/L2/L3/L4
ISSUES: 问题列表
REVISION_SUGGESTIONS: 修改建议
""",
                expected_output="PE级审核结果",
                agent=reviewer
            )
            
            crew = Crew(
                agents=[reviewer],
                tasks=[review_task],
                process=Process.sequential,
                verbose=self.verbose
            )
            
            result = crew.kickoff()
            review_output = str(result)
            
            # 解析审核结果
            review_result = parse_reviewer_output(review_output)
            
            print(f"      评分: {review_result.get('score', 'N/A')}/100")
            
            if not review_result.get("need_revision", False):
                print(f"   ✓ PE级审核通过")
                self.state["quality_passed"] = True
                break
            
            # 需要修订
            print(f"      需要修订，进行第 {revision + 1} 次修改...")
            
            issues = review_result.get("issues", [])
            suggestions = review_result.get("revision_suggestions", [])
            
            if issues or suggestions:
                current_report = self._revise_report_pe(
                    current_report, issues, suggestions,
                    industry, province, target_year
                )
        
        return current_report
    
    def _revise_report_pe(self, report: str, issues: List[str],
                          suggestions: List[str], industry: str,
                          province: str, target_year: str) -> str:
        """PE级报告修订"""
        
        writer = Agent(
            role="PE级研究报告修订专家",
            goal="根据PE级审核意见修订报告",
            backstory="你是一位经验丰富的PE级研究报告修订专家，擅长根据审核意见提升报告质量。",
            llm=self.model_name,
            verbose=self.verbose
        )
        
        revision_task = Task(
            description=f"""
请根据PE级审核意见修订以下报告：

【原报告】
{report[:10000]}

【审核问题】
{chr(10).join(issues) if issues else '无具体问题'}

【修改建议】
{chr(10).join(suggestions) if suggestions else '无具体建议'}

【修订要求】
1. 保持报告整体结构不变
2. 针对性修改问题部分
3. 补充缺失的PE级内容（标的深拆、估值、风险、反共识）
4. 确保修改后达到PE级标准

请输出修订后的完整报告。
""",
            expected_output="修订后的PE级报告",
            agent=writer
        )
        
        crew = Crew(
            agents=[writer],
            tasks=[revision_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        return str(result)
    
    def _enhance_report(self, report: str, scorecard, 
                        industry: str, province: str, target_year: str) -> str:
        """根据评分补强报告"""
        
        # 获取补强清单
        enhancements = []
        for item in scorecard.enhancement_checklist[:5]:
            enhancements.append(item["item"])
        
        if not enhancements:
            return report
        
        writer = Agent(
            role="研究报告补强专家",
            goal="根据评分补强研究报告",
            backstory="你是一位专业的研究报告补强专家，擅长针对性提升报告质量。",
            llm=self.model_name,
            verbose=self.verbose
        )
        
        enhance_task = Task(
            description=f"""
请根据以下补强清单改进报告：

【原报告】
{report[:10000]}

【补强清单】
{chr(10).join(f"- {e}" for e in enhancements)}

【关键缺失】
{chr(10).join(f"- {g}" for g in scorecard.critical_gaps)}

【补强要求】
1. 针对性补充缺失内容
2. 保持报告整体结构
3. 确保补充内容专业准确

请输出补强后的完整报告。
""",
            expected_output="补强后的报告",
            agent=writer
        )
        
        crew = Crew(
            agents=[writer],
            tasks=[enhance_task],
            process=Process.sequential,
            verbose=self.verbose
        )
        
        result = crew.kickoff()
        return str(result)
    
    def _save_report(self, report: str, industry: str, 
                     province: str, target_year: str) -> str:
        """保存报告"""
        
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"{target_year}_{province}_{industry}_PE级行业研究报告_{date_str}.md"
        output_path = os.path.join(output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return output_path
    
    def _save_scorecard(self, scorecard, industry: str,
                        province: str, target_year: str) -> str:
        """保存评分报告"""
        
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"{target_year}_{province}_{industry}_评分报告_{date_str}.md"
        output_path = os.path.join(output_dir, filename)
        
        report = scorecard.generate_scorecard_report()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return output_path


# 便捷函数
def run_industry_research_v3(industry: str, province: str, 
                              target_year: str = "2025",
                              focus: str = "综合分析",
                              model_name: str = "gpt-4o-mini",
                              max_revisions: int = 2,
                              key_companies: List[str] = None) -> Dict[str, Any]:
    """
    运行PE级行业研究 V3.0
    
    Args:
        industry: 行业名称
        province: 省份
        target_year: 目标年份
        focus: 研究侧重点
        model_name: LLM模型
        max_revisions: 最大修订次数
        key_companies: 重点分析的公司列表
    
    Returns:
        Dict: 研究结果，包含PE级评分
    """
    workflow = IndustryResearchWorkflowV3(model_name=model_name)
    return workflow.run(
        industry, province, target_year, focus, 
        max_revisions, key_companies
    )
