# agent_system/workflows/industry_research_v2.py
"""
行业研究工作流 V2.0
整合所有升级模块，实现投研级Agent

核心升级：
1. 架构模式 - 动态图模式，支持循环反馈
2. RAG深度 - Agentic RAG，查询改写+重排序+自省
3. 数据严谨性 - Python代码执行器，计算型分析
4. Memory系统 - 事实核查，全局上下文共享
"""

import os
import re
import datetime
from typing import Dict, List, Optional, Any

# CrewAI核心
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# 自定义模块
from agent_system.prompts.planner_prompt import get_planner_prompt
from agent_system.prompts.researcher_prompt import get_researcher_prompt
from agent_system.prompts.analyst_prompt import get_analyst_prompt
from agent_system.prompts.writer_prompt import get_writer_prompt
from agent_system.prompts.reviewer_prompt import get_reviewer_prompt

# 增强模块
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


class IndustryResearchWorkflowV2:
    """
    行业研究工作流 V2.0
    支持动态规划、循环反馈、数据质量把关
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
        self.search_tool = SerperDevTool(n_results=8)
        
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
            "quality_passed": False
        }
    
    def run(self, industry: str, province: str, target_year: str = "2025",
            focus: str = "综合分析", max_revisions: int = 2) -> Dict[str, Any]:
        """
        运行行业研究工作流
        
        Args:
            industry: 行业名称
            province: 省份
            target_year: 目标年份
            focus: 研究侧重点
            max_revisions: 最大修订次数
        
        Returns:
            Dict: 研究结果
        """
        print(f"\n{'='*60}")
        print(f"🚀 启动行业研究工作流 V2.0")
        print(f"   行业: {industry} | 区域: {province} | 年份: {target_year}")
        print(f"   侧重: {focus} | 最大修订: {max_revisions}次")
        print(f"{'='*60}\n")
        
        # 初始化全局上下文
        global_context_manager.init_context(industry, province, target_year, focus)
        
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
            print("\n📋 Phase 1: 研究规划")
            plan = self._phase_planning(industry, province, target_year, focus)
            
            # Phase 2: 研究（带数据质量检查）
            print("\n🔍 Phase 2: 数据研究")
            research_data = self._phase_research_with_quality(
                industry, province, target_year, focus, plan
            )
            
            # Phase 3: 分析
            print("\n📊 Phase 3: 深度分析")
            analysis = self._phase_analysis(
                industry, province, target_year, focus, research_data
            )
            
            # Phase 4: 写作
            print("\n✍️ Phase 4: 报告撰写")
            report = self._phase_writing(
                industry, province, target_year, focus, research_data, analysis
            )
            
            # Phase 5: 审核与修订（循环）
            print("\n🔄 Phase 5: 审核与修订")
            final_report = self._phase_review_and_revise(
                industry, province, target_year, focus,
                report, research_data, analysis, max_revisions
            )
            
            # 结束会话
            quality_score = self.state.get("data_coverage", 0.8)
            if enhanced_memory:
                enhanced_memory.end_session(final_report, quality_score)
            
            # 保存报告
            output_path = self._save_report(final_report, industry, province, target_year)
            
            print(f"\n{'='*60}")
            print(f"✅ 研究完成!")
            print(f"   报告路径: {output_path}")
            print(f"   数据覆盖率: {quality_score:.1%}")
            print(f"{'='*60}\n")
            
            return {
                "success": True,
                "report": final_report,
                "output_path": output_path,
                "quality_score": quality_score,
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
    
    def _phase_planning(self, industry: str, province: str, 
                        target_year: str, focus: str) -> str:
        """Phase 1: 研究规划"""
        
        # 获取历史研究建议
        suggestions = ""
        if memory_manager:
            try:
                context = memory_manager.get_industry_context(industry, province)
                if context:
                    suggestions = f"\n\n【历史研究经验】\n{context}"
            except:
                pass
        
        planner = Agent(
            role="研究规划师",
            goal=f"为{province}{industry}行业研究制定详细的研究计划",
            backstory=get_planner_prompt(),
            llm=self.model_name,
            verbose=self.verbose
        )
        
        planning_task = Task(
            description=f"""
请为以下研究项目制定详细的研究计划：

【研究主题】
- 行业：{industry}
- 区域：{province}
- 目标年份：{target_year}
- 研究侧重：{focus}
{suggestions}

【计划要求】
1. 明确研究目标和范围
2. 列出需要收集的关键数据点
3. 规划研究的主要章节结构
4. 识别潜在的数据来源
5. 预估研究重点和难点

请输出结构化的研究计划。
""",
            expected_output="详细的研究计划，包含目标、数据需求、章节结构、数据来源",
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
        
        print(f"   ✓ 研究计划已生成")
        
        return plan
    
    def _phase_research_with_quality(self, industry: str, province: str,
                                      target_year: str, focus: str, 
                                      plan: str) -> str:
        """Phase 2: 带数据质量检查的研究"""
        
        researcher = Agent(
            role="资深行业研究员",
            goal=f"收集{province}{industry}行业的全面数据",
            backstory=get_researcher_prompt(),
            tools=self.enhanced_tools,
            llm=self.model_name,
            verbose=self.verbose
        )
        
        # 构建研究任务，注入全局上下文
        context_prompt = global_context_manager.export_context_prompt()
        
        research_task = Task(
            description=f"""
根据研究计划，收集{province}{industry}行业的全面数据。

【研究计划】
{plan}

【全局上下文】
{context_prompt}

【数据收集要求】
1. 市场规模数据（必须包含具体数字和来源）
2. 增长率数据（CAGR、同比增速）
3. 产业链信息（上中下游企业和分布）
4. 竞争格局（龙头企业、市场份额）
5. 政策环境（国家和地方政策）
6. 投融资信息（近期融资事件）

【工具使用指南】
- 使用 Market Size Search Enhanced 搜索市场规模
- 使用 Industry Policy Search Enhanced 搜索政策
- 使用 Financial Data Search 搜索企业财务
- 使用 Competitive Analysis Search 搜索竞争格局
- 使用 Supply Chain Search Enhanced 搜索产业链
- 使用 Python Code Executor 进行数据计算

请确保每个数据点都标注来源。
""",
            expected_output="全面的行业数据报告，包含市场规模、增长率、产业链、竞争格局、政策、投融资等",
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
        
        print(f"   ✓ 数据收集完成")
        print(f"   📊 数据覆盖率: {quality.total_score:.1%}")
        
        # 如果数据不足，进行补充研究
        if quality.total_score < 0.6 and self.state["iteration"] < self.state["max_iterations"]:
            print(f"   ⚠️ 数据覆盖不足，进行补充研究...")
            
            # 获取路由建议
            route = self.quality_router.route(quality)
            
            if route["action"] == "supplement":
                supplement_data = self._supplement_research(
                    industry, province, target_year, 
                    route["missing_dimensions"]
                )
                research_data = research_data + "\n\n【补充数据】\n" + supplement_data
                
                # 重新检查
                quality = data_quality_checker.check_coverage(research_data)
                self.state["data_coverage"] = quality.total_score
                print(f"   📊 补充后覆盖率: {quality.total_score:.1%}")
        
        # 注册关键事实到全局上下文
        self._extract_and_register_facts(research_data, "Researcher")
        
        return research_data
    
    def _supplement_research(self, industry: str, province: str,
                              target_year: str, 
                              missing_dimensions: List[str]) -> str:
        """补充研究"""
        self.state["iteration"] += 1
        
        supplement_queries = []
        for dim in missing_dimensions:
            if "市场规模" in dim:
                supplement_queries.append(f"{province} {industry} 市场规模 {target_year}")
            elif "增长率" in dim:
                supplement_queries.append(f"{industry} 增速 CAGR 预测")
            elif "产业链" in dim:
                supplement_queries.append(f"{industry} 产业链 上游 中游 下游")
            elif "竞争" in dim:
                supplement_queries.append(f"{industry} 龙头企业 市场份额 CR5")
            elif "政策" in dim:
                supplement_queries.append(f"{province} {industry} 产业政策 补贴")
        
        results = []
        for query in supplement_queries[:3]:  # 限制查询数量
            try:
                result = self.search_tool.run(query)
                if result:
                    results.append(f"【{query}】\n{result}")
            except:
                pass
        
        return "\n\n".join(results)
    
    def _extract_and_register_facts(self, content: str, agent: str):
        """从内容中提取事实并注册到全局上下文"""
        
        # 提取市场规模
        market_patterns = [
            r'市场规模[：:约为达到]\s*([\d,\.]+)\s*(亿|万)',
            r'规模[：:约为达到]\s*([\d,\.]+)\s*(亿|万)',
        ]
        for pattern in market_patterns:
            match = re.search(pattern, content)
            if match:
                value = match.group(1).replace(",", "")
                unit = match.group(2)
                global_context_manager.register_fact(
                    "市场规模",
                    f"{value}{unit}元",
                    f"Agent:{agent}",
                    agent
                )
                break
        
        # 提取增长率
        growth_patterns = [
            r'增[长速][率度][：:约为达到]\s*([\d\.]+)\s*%',
            r'CAGR[：:约为达到]\s*([\d\.]+)\s*%',
        ]
        for pattern in growth_patterns:
            match = re.search(pattern, content)
            if match:
                value = match.group(1)
                global_context_manager.register_fact(
                    "增长率",
                    f"{value}%",
                    f"Agent:{agent}",
                    agent
                )
                break
    
    def _phase_analysis(self, industry: str, province: str,
                        target_year: str, focus: str, 
                        research_data: str) -> str:
        """Phase 3: 深度分析"""
        
        # 获取全局上下文
        context_prompt = global_context_manager.export_context_prompt()
        
        analyst = Agent(
            role="资深行业分析师",
            goal=f"对{province}{industry}行业进行深度分析",
            backstory=get_analyst_prompt(),
            tools=[code_executor_tool],  # 分析师可以使用代码执行器
            llm=self.model_name,
            verbose=self.verbose
        )
        
        analysis_task = Task(
            description=f"""
基于收集的数据，对{province}{industry}行业进行深度分析。

【研究数据】
{research_data[:8000]}

【全局上下文（确保数据一致性）】
{context_prompt}

【分析要求】
1. 市场规模分析
   - 当前规模和历史趋势
   - 增长驱动因素
   - 未来预测（可使用Python计算CAGR）

2. 产业链分析
   - 上中下游结构
   - 价值分配
   - 关键环节

3. 竞争格局分析
   - 市场集中度（CR5/CR10）
   - 龙头企业分析
   - 竞争壁垒

4. 投资价值分析
   - 投资机会
   - 风险因素
   - 估值水平

请确保分析中的数据与全局上下文一致。
""",
            expected_output="深度分析报告，包含市场、产业链、竞争、投资分析",
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
        
        print(f"   ✓ 深度分析完成")
        
        return analysis
    
    def _phase_writing(self, industry: str, province: str,
                       target_year: str, focus: str,
                       research_data: str, analysis: str) -> str:
        """Phase 4: 报告撰写"""
        
        # 获取全局上下文
        context_prompt = global_context_manager.export_context_prompt()
        
        writer = Agent(
            role="资深研究报告撰写专家",
            goal=f"撰写{province}{industry}行业研究报告",
            backstory=get_writer_prompt(),
            llm=self.model_name,
            verbose=self.verbose
        )
        
        writing_task = Task(
            description=f"""
基于研究数据和分析结果，撰写专业的行业研究报告。

【研究数据摘要】
{research_data[:5000]}

【分析结果】
{analysis[:5000]}

【全局上下文（确保数据一致性）】
{context_prompt}

【报告结构要求】
1. 摘要（核心观点和投资建议）
2. 行业概述
3. 市场规模与增长
4. 产业链分析
5. 竞争格局
6. 政策环境
7. 投资建议
8. 风险提示

【写作要求】
- 使用专业的投研报告语言
- 数据必须标注来源
- 确保数据与全局上下文一致
- 图表建议使用Markdown表格
- 字数要求：8000-12000字
""",
            expected_output="完整的行业研究报告，Markdown格式",
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
        
        print(f"   ✓ 报告撰写完成")
        
        return report
    
    def _phase_review_and_revise(self, industry: str, province: str,
                                  target_year: str, focus: str,
                                  report: str, research_data: str,
                                  analysis: str, max_revisions: int) -> str:
        """Phase 5: 审核与修订（循环）"""
        
        current_report = report
        
        for revision in range(max_revisions):
            print(f"   📝 第 {revision + 1} 轮审核...")
            
            # 事实核查
            if fact_validation:
                passed, corrected, issues = fact_validation.validate_before_write(
                    current_report, "Writer"
                )
                if not passed:
                    print(f"      ⚠️ 发现 {len(issues)} 个数据一致性问题")
                    current_report = corrected
            
            # 审核
            reviewer = Agent(
                role="研究报告审核专家",
                goal="审核研究报告的质量和准确性",
                backstory=get_reviewer_prompt(),
                llm=self.model_name,
                verbose=self.verbose
            )
            
            review_task = Task(
                description=f"""
请审核以下行业研究报告：

【报告内容】
{current_report[:10000]}

【审核要点】
1. 数据准确性 - 数字是否有来源支撑
2. 逻辑完整性 - 分析是否有理有据
3. 结构规范性 - 是否符合投研报告标准
4. 语言专业性 - 是否使用专业术语

【输出格式】
REVIEW_RESULT: PASS 或 NEED_REVISION
SCORE: XX/100
ISSUES: 问题列表（如有）
REVISION_SUGGESTIONS: 修改建议（如有）
""",
                expected_output="审核结果，包含评分和修改建议",
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
                print(f"   ✓ 审核通过")
                self.state["quality_passed"] = True
                break
            
            # 需要修订
            print(f"      需要修订，进行第 {revision + 1} 次修改...")
            
            issues = review_result.get("issues", [])
            suggestions = review_result.get("revision_suggestions", [])
            
            if issues or suggestions:
                current_report = self._revise_report(
                    current_report, issues, suggestions,
                    industry, province, target_year
                )
        
        return current_report
    
    def _revise_report(self, report: str, issues: List[str],
                       suggestions: List[str], industry: str,
                       province: str, target_year: str) -> str:
        """修订报告"""
        
        writer = Agent(
            role="研究报告修订专家",
            goal="根据审核意见修订报告",
            backstory="你是一位经验丰富的研究报告修订专家，擅长根据审核意见改进报告质量。",
            llm=self.model_name,
            verbose=self.verbose
        )
        
        revision_task = Task(
            description=f"""
请根据审核意见修订以下报告：

【原报告】
{report[:8000]}

【审核问题】
{chr(10).join(issues) if issues else '无具体问题'}

【修改建议】
{chr(10).join(suggestions) if suggestions else '无具体建议'}

【修订要求】
1. 保持报告整体结构不变
2. 针对性修改问题部分
3. 补充缺失的数据或分析
4. 确保修改后的内容专业准确

请输出修订后的完整报告。
""",
            expected_output="修订后的完整报告",
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
    
    def _save_report(self, report: str, industry: str, 
                     province: str, target_year: str) -> str:
        """保存报告"""
        
        # 创建输出目录
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"{target_year}_{province}_{industry}_行业研究报告_{date_str}.md"
        output_path = os.path.join(output_dir, filename)
        
        # 保存报告
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return output_path


# 便捷函数
def run_industry_research_v2(industry: str, province: str, 
                              target_year: str = "2025",
                              focus: str = "综合分析",
                              model_name: str = "gpt-4o-mini",
                              max_revisions: int = 2) -> Dict[str, Any]:
    """
    运行行业研究 V2.0
    
    Args:
        industry: 行业名称
        province: 省份
        target_year: 目标年份
        focus: 研究侧重点
        model_name: LLM模型
        max_revisions: 最大修订次数
    
    Returns:
        Dict: 研究结果
    """
    workflow = IndustryResearchWorkflowV2(model_name=model_name)
    return workflow.run(industry, province, target_year, focus, max_revisions)
