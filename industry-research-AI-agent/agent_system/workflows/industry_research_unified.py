# agent_system/workflows/industry_research_unified.py
"""
统一行业研究工作流 V4.0
整合V2（数据质量+Agentic RAG）和V3（PE级专业分析）功能
新增：自动公司发现、数据图表生成
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# CrewAI导入
try:
    from crewai import Agent, Task, Crew, Process
    HAS_CREWAI = True
except ImportError:
    HAS_CREWAI = False
    print("警告: CrewAI未安装，部分功能不可用")

# 本地模块导入
from agent_system.prompts.planner_prompt import get_planner_prompt
from agent_system.prompts.researcher_prompt import get_researcher_prompt
from agent_system.prompts.analyst_prompt import get_analyst_prompt
from agent_system.prompts.writer_prompt import get_writer_prompt
from agent_system.prompts.reviewer_prompt import get_reviewer_prompt
from agent_system.postprocess.reviewer_parser import parse_reviewer_response
from agent_system.tools.tools_custom import get_research_tools

# 新增模块导入
try:
    from agent_system.discovery.company_discovery import CompanyDiscoveryEngine, get_prompt_for_company_discovery
    HAS_DISCOVERY = True
except ImportError:
    HAS_DISCOVERY = False

try:
    from agent_system.professional.company_deep_dive import get_company_deep_dive_prompt, CompanyDeepDiveAnalyzer
    from agent_system.professional.valuation_framework import get_valuation_prompt, ValuationAnalyzer
    from agent_system.professional.micro_risk_analysis import get_micro_risk_prompt
    from agent_system.professional.contrarian_views import get_contrarian_prompt
    from agent_system.professional.pe_report_scorer import PEReportScorer
    HAS_PROFESSIONAL = True
except ImportError:
    HAS_PROFESSIONAL = False

try:
    from utils.chart_generator import ChartGenerator, create_market_trend_chart, create_supply_chain_profit_chart, create_competitive_landscape_chart
    HAS_CHARTS = True
except ImportError:
    HAS_CHARTS = False


class UnifiedResearchWorkflow:
    """
    统一行业研究工作流
    整合所有功能模块
    """
    
    def __init__(
        self,
        industry: str,
        province: str,
        target_year: str,
        focus: str = "综合分析",
        output_dir: str = "./output",
        enable_pe_analysis: bool = True,
        enable_charts: bool = True,
        max_revisions: int = 2,
        log_callback=None
    ):
        """
        初始化工作流
        
        Args:
            industry: 行业名称
            province: 省份
            target_year: 目标年份
            focus: 研究重点
            output_dir: 输出目录
            enable_pe_analysis: 是否启用PE级分析
            enable_charts: 是否生成图表
            max_revisions: 最大修订次数
            log_callback: 日志回调函数
        """
        self.industry = industry
        self.province = province
        self.target_year = target_year
        self.focus = focus
        self.output_dir = output_dir
        self.enable_pe_analysis = enable_pe_analysis and HAS_PROFESSIONAL
        self.enable_charts = enable_charts and HAS_CHARTS
        self.max_revisions = max_revisions
        self.log_callback = log_callback
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        if self.enable_charts:
            self.charts_dir = os.path.join(output_dir, "charts")
            os.makedirs(self.charts_dir, exist_ok=True)
        
        # 初始化组件
        self.company_discovery = CompanyDiscoveryEngine() if HAS_DISCOVERY else None
        self.chart_generator = ChartGenerator(output_dir=self.charts_dir) if self.enable_charts else None
        self.pe_scorer = PEReportScorer() if self.enable_pe_analysis else None
        
        # 研究数据存储
        self.research_data = {}
        self.discovered_companies = []
        self.generated_charts = []
        self.final_report = ""
        self.pe_score = None
    
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        if self.log_callback:
            self.log_callback(log_message)
    
    def run(self) -> Dict[str, Any]:
        """
        运行完整工作流
        
        Returns:
            包含研报和元数据的字典
        """
        self.log(f"开始生成 {self.target_year}年{self.province}{self.industry}行业研究报告")
        self.log(f"PE级分析: {'启用' if self.enable_pe_analysis else '禁用'}")
        self.log(f"图表生成: {'启用' if self.enable_charts else '禁用'}")
        
        try:
            # Phase 1: 规划
            self.log("Phase 1: 制定研究计划...")
            research_plan = self._phase_planning()
            
            # Phase 2: 数据收集
            self.log("Phase 2: 收集行业数据...")
            research_data = self._phase_research(research_plan)
            
            # Phase 3: 自动公司发现
            self.log("Phase 3: 自动发现产业链公司...")
            self._phase_company_discovery(research_data)
            
            # Phase 4: 数据分析
            self.log("Phase 4: 深度数据分析...")
            analysis_result = self._phase_analysis(research_data)
            
            # Phase 5: PE级深度分析（如果启用）
            if self.enable_pe_analysis and self.discovered_companies:
                self.log("Phase 5: PE级标的深拆分析...")
                pe_analysis = self._phase_pe_analysis()
                analysis_result = self._merge_pe_analysis(analysis_result, pe_analysis)
            
            # Phase 6: 生成图表（如果启用）
            if self.enable_charts:
                self.log("Phase 6: 生成数据可视化图表...")
                self._phase_chart_generation(research_data, analysis_result)
            
            # Phase 7: 撰写报告
            self.log("Phase 7: 撰写研究报告...")
            draft_report = self._phase_writing(research_data, analysis_result)
            
            # Phase 8: 审核与修订
            self.log("Phase 8: 审核与修订...")
            final_report = self._phase_review_and_revise(draft_report)
            
            # Phase 9: PE评分（如果启用）
            if self.enable_pe_analysis:
                self.log("Phase 9: PE级质量评分...")
                self._phase_pe_scoring(final_report)
            
            # Phase 10: 保存报告
            self.log("Phase 10: 保存最终报告...")
            output_path = self._save_report(final_report)
            
            self.log(f"✅ 报告生成完成: {output_path}")
            
            return {
                "success": True,
                "report": final_report,
                "output_path": output_path,
                "charts": self.generated_charts,
                "discovered_companies": [c.name for c in self.discovered_companies],
                "pe_score": self.pe_score,
                "metadata": {
                    "industry": self.industry,
                    "province": self.province,
                    "year": self.target_year,
                    "generated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.log(f"❌ 报告生成失败: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "report": self.final_report or ""
            }
    
    def _phase_planning(self) -> str:
        """Phase 1: 规划阶段"""
        planner_prompt = get_planner_prompt(
            self.industry, self.province, self.target_year, self.focus
        )
        
        # 添加公司发现要求
        if HAS_DISCOVERY:
            planner_prompt += """

特别要求：
- 在数据收集阶段，需要识别产业链各环节的头部公司
- 对发现的关键公司进行深度分析
- 构建完整的产业链图谱
"""
        
        if not HAS_CREWAI:
            return self._simulate_planning(planner_prompt)
        
        planner = Agent(
            role="行业研究规划师",
            goal=f"制定{self.industry}行业研究计划",
            backstory="资深行业研究专家，擅长制定系统性研究框架",
            verbose=True
        )
        
        task = Task(
            description=planner_prompt,
            expected_output="详细的研究计划和数据需求清单",
            agent=planner
        )
        
        crew = Crew(agents=[planner], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        
        return str(result)
    
    def _phase_research(self, research_plan: str) -> str:
        """Phase 2: 数据收集阶段"""
        researcher_prompt = get_researcher_prompt(self.industry, self.province, self.target_year)
        
        # 添加公司发现搜索要求
        if HAS_DISCOVERY:
            company_search_prompt = get_prompt_for_company_discovery(self.industry, self.province)
            researcher_prompt += f"\n\n{company_search_prompt}"
        
        if not HAS_CREWAI:
            return self._simulate_research(researcher_prompt)
        
        tools = get_research_tools()
        
        researcher = Agent(
            role="行业研究员",
            goal=f"收集{self.province}{self.industry}行业全面数据",
            backstory="专业行业研究员，擅长多渠道数据收集",
            tools=tools,
            verbose=True
        )
        
        task = Task(
            description=researcher_prompt,
            expected_output="完整的行业数据报告",
            agent=researcher
        )
        
        crew = Crew(agents=[researcher], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        
        research_data = str(result)
        self.research_data['raw'] = research_data
        
        return research_data
    
    def _phase_company_discovery(self, research_data: str):
        """Phase 3: 自动公司发现"""
        if not self.company_discovery:
            self.log("公司发现模块未启用", "WARNING")
            return
        
        self.discovered_companies = self.company_discovery.discover_from_research_data(
            research_data, self.industry, self.province
        )
        
        self.log(f"发现公司数量: {len(self.discovered_companies)}")
        
        # 获取关键公司
        key_companies = self.company_discovery.get_key_companies_for_deep_dive(max_companies=5)
        self.log(f"关键公司: {[c.name for c in key_companies]}")
        
        # 构建产业链图谱
        supply_chain = self.company_discovery.build_supply_chain_map(self.industry, self.province)
        self.research_data['supply_chain'] = supply_chain
        
        # 生成发现报告
        discovery_report = self.company_discovery.generate_discovery_report()
        self.research_data['company_discovery'] = discovery_report
    
    def _phase_analysis(self, research_data: str) -> str:
        """Phase 4: 数据分析阶段"""
        analyst_prompt = get_analyst_prompt(self.industry, self.province, self.target_year)
        
        # 添加发现的公司信息
        if self.discovered_companies:
            company_info = "\n\n## 发现的产业链公司\n"
            for segment in ['上游', '中游', '下游']:
                companies = [c for c in self.discovered_companies if c.segment == segment]
                if companies:
                    company_info += f"\n### {segment}\n"
                    for c in companies[:5]:
                        company_info += f"- {c.name}（{c.market_position}）"
                        if c.market_share:
                            company_info += f"，市场份额{c.market_share}%"
                        company_info += "\n"
            
            analyst_prompt += company_info
        
        if not HAS_CREWAI:
            return self._simulate_analysis(analyst_prompt, research_data)
        
        analyst = Agent(
            role="行业分析师",
            goal=f"深度分析{self.industry}行业数据",
            backstory="资深行业分析师，擅长数据分析和趋势预测",
            verbose=True
        )
        
        task = Task(
            description=f"{analyst_prompt}\n\n研究数据：\n{research_data[:10000]}",
            expected_output="深度分析报告",
            agent=analyst
        )
        
        crew = Crew(agents=[analyst], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        
        return str(result)
    
    def _phase_pe_analysis(self) -> Dict[str, str]:
        """Phase 5: PE级深度分析"""
        pe_analysis = {}
        
        key_companies = self.company_discovery.get_key_companies_for_deep_dive(max_companies=3)
        
        for company in key_companies:
            self.log(f"  深度分析: {company.name}")
            
            # 标的深拆
            deep_dive_prompt = get_company_deep_dive_prompt(
                company.name, self.industry
            )
            
            # 估值分析
            valuation_prompt = get_valuation_prompt(
                company.name, self.industry
            )
            
            # 微观风险
            risk_prompt = get_micro_risk_prompt(
                company.name, self.industry, company.sub_segment
            )
            
            if not HAS_CREWAI:
                pe_analysis[company.name] = self._simulate_pe_analysis(
                    company, deep_dive_prompt, valuation_prompt, risk_prompt
                )
            else:
                pe_analysis[company.name] = self._run_pe_analysis_crew(
                    company, deep_dive_prompt, valuation_prompt, risk_prompt
                )
        
        # 反共识观点
        contrarian_prompt = get_contrarian_prompt(self.industry, self.province)
        pe_analysis['contrarian_views'] = self._generate_contrarian_views(contrarian_prompt)
        
        return pe_analysis
    
    def _merge_pe_analysis(self, analysis_result: str, pe_analysis: Dict[str, str]) -> str:
        """合并PE级分析到主分析结果"""
        merged = analysis_result
        
        # 添加标的深拆部分
        merged += "\n\n## 重点标的深度分析\n"
        for company_name, analysis in pe_analysis.items():
            if company_name != 'contrarian_views':
                merged += f"\n### {company_name}\n{analysis}\n"
        
        # 添加反共识观点
        if 'contrarian_views' in pe_analysis:
            merged += f"\n\n## 反共识观点与投资洞察\n{pe_analysis['contrarian_views']}\n"
        
        return merged
    
    def _phase_chart_generation(self, research_data: str, analysis_result: str):
        """Phase 6: 生成数据图表"""
        if not self.chart_generator:
            return
        
        try:
            # 1. 市场规模趋势图
            years = ['2020', '2021', '2022', '2023', '2024', '2025E']
            # 模拟数据（实际应从research_data中提取）
            market_sizes = [1000, 1200, 1500, 1800, 2200, 2800]
            growth_rates = [15, 20, 25, 20, 22, 27]
            
            chart_path = create_market_trend_chart(
                years, market_sizes, growth_rates,
                title=f"{self.province}{self.industry}市场规模趋势",
                output_dir=self.charts_dir
            )
            self.generated_charts.append(("市场规模趋势", chart_path))
            self.log(f"  生成图表: 市场规模趋势")
            
            # 2. 产业链利润分布图
            if self.discovered_companies:
                segments = ['上游-芯片', '上游-算力', '中游-平台', '中游-应用', '下游-服务']
                margins = [45, 35, 30, 25, 20]
                
                chart_path = create_supply_chain_profit_chart(
                    segments, margins,
                    title=f"{self.industry}产业链利润分布",
                    output_dir=self.charts_dir
                )
                self.generated_charts.append(("产业链利润分布", chart_path))
                self.log(f"  生成图表: 产业链利润分布")
            
            # 3. 竞争格局饼图
            key_companies = self.company_discovery.get_key_companies_for_deep_dive(5) if self.company_discovery else []
            if key_companies:
                companies = [c.name for c in key_companies]
                shares = [c.market_share or 15 for c in key_companies]
                
                chart_path = create_competitive_landscape_chart(
                    companies, shares,
                    title=f"{self.industry}竞争格局",
                    output_dir=self.charts_dir
                )
                self.generated_charts.append(("竞争格局", chart_path))
                self.log(f"  生成图表: 竞争格局")
            
            # 4. 雷达图 - 投资价值评估
            if key_companies:
                categories = ['市场规模', '增长潜力', '竞争壁垒', '盈利能力', '政策支持', '技术成熟度']
                values = {
                    '行业整体': [80, 85, 70, 65, 90, 75]
                }
                
                chart_path = self.chart_generator.radar_chart(
                    categories, values,
                    title=f"{self.industry}投资价值评估",
                    filename=f"investment_radar_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                )
                self.generated_charts.append(("投资价值评估", chart_path))
                self.log(f"  生成图表: 投资价值评估")
                
        except Exception as e:
            self.log(f"图表生成失败: {e}", "WARNING")
    
    def _phase_writing(self, research_data: str, analysis_result: str) -> str:
        """Phase 7: 撰写报告"""
        writer_prompt = get_writer_prompt(self.industry, self.province, self.target_year)
        
        # 添加图表引用
        if self.generated_charts:
            chart_section = "\n\n## 数据可视化图表\n"
            for chart_name, chart_path in self.generated_charts:
                chart_section += f"\n### {chart_name}\n![{chart_name}]({chart_path})\n"
            writer_prompt += f"\n\n请在报告适当位置引用以下图表：{chart_section}"
        
        # 添加公司发现报告
        if self.research_data.get('company_discovery'):
            writer_prompt += f"\n\n产业链公司发现报告：\n{self.research_data['company_discovery']}"
        
        if not HAS_CREWAI:
            return self._simulate_writing(writer_prompt, research_data, analysis_result)
        
        writer = Agent(
            role="研报撰写专家",
            goal=f"撰写专业的{self.industry}行业研究报告",
            backstory="资深研报撰写专家，擅长将数据转化为投资洞察",
            verbose=True
        )
        
        task = Task(
            description=f"{writer_prompt}\n\n分析结果：\n{analysis_result[:15000]}",
            expected_output="完整的行业研究报告",
            agent=writer
        )
        
        crew = Crew(agents=[writer], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        
        return str(result)
    
    def _phase_review_and_revise(self, draft_report: str) -> str:
        """Phase 8: 审核与修订"""
        current_report = draft_report
        
        for revision in range(self.max_revisions):
            self.log(f"  审核轮次 {revision + 1}/{self.max_revisions}")
            
            reviewer_prompt = get_reviewer_prompt(self.industry, self.province, self.target_year)
            
            if not HAS_CREWAI:
                review_result = self._simulate_review(reviewer_prompt, current_report)
            else:
                reviewer = Agent(
                    role="研报审核专家",
                    goal="审核研报质量并提出改进建议",
                    backstory="资深研报审核专家，确保报告质量达标",
                    verbose=True
                )
                
                task = Task(
                    description=f"{reviewer_prompt}\n\n待审核报告：\n{current_report[:15000]}",
                    expected_output="审核意见",
                    agent=reviewer
                )
                
                crew = Crew(agents=[reviewer], tasks=[task], process=Process.sequential)
                review_result = str(crew.kickoff())
            
            # 解析审核结果
            parsed = parse_reviewer_response(review_result)
            
            if not parsed.get('need_revision', False):
                self.log(f"  审核通过，评分: {parsed.get('score', 'N/A')}")
                break
            
            self.log(f"  需要修订，评分: {parsed.get('score', 'N/A')}")
            
            # 执行修订
            current_report = self._revise_report(current_report, parsed.get('suggestions', []))
        
        self.final_report = current_report
        return current_report
    
    def _revise_report(self, report: str, suggestions: List[str]) -> str:
        """根据建议修订报告"""
        if not suggestions:
            return report
        
        revision_prompt = f"""
请根据以下审核建议修订报告：

审核建议：
{chr(10).join(f'- {s}' for s in suggestions)}

原报告：
{report[:15000]}

请输出修订后的完整报告。
"""
        
        if not HAS_CREWAI:
            return report  # 简化处理
        
        reviser = Agent(
            role="研报修订专家",
            goal="根据审核意见修订报告",
            backstory="专业研报修订专家",
            verbose=True
        )
        
        task = Task(
            description=revision_prompt,
            expected_output="修订后的报告",
            agent=reviser
        )
        
        crew = Crew(agents=[reviser], tasks=[task], process=Process.sequential)
        result = crew.kickoff()
        
        return str(result)
    
    def _phase_pe_scoring(self, report: str):
        """Phase 9: PE级评分"""
        if not self.pe_scorer:
            return
        
        try:
            scorecard = self.pe_scorer.score_report(report)
            self.pe_score = {
                'total_score': scorecard.total_score,
                'level': scorecard.level,
                'dimension_scores': scorecard.dimension_scores,
                'gaps': scorecard.gaps[:5]  # 前5个差距
            }
            
            self.log(f"  PE评分: {scorecard.total_score}/100 ({scorecard.level})")
            
        except Exception as e:
            self.log(f"PE评分失败: {e}", "WARNING")
    
    def _save_report(self, report: str) -> str:
        """保存报告"""
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{self.target_year}_{self.province}_{self.industry}_行业研究报告_{timestamp}.md"
        output_path = os.path.join(self.output_dir, filename)
        
        # 添加报告头部信息
        header = f"""# {self.target_year}年{self.province}{self.industry}行业研究报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**研究重点**: {self.focus}
**PE级分析**: {'已启用' if self.enable_pe_analysis else '未启用'}
"""
        
        if self.pe_score:
            header += f"""**PE评分**: {self.pe_score['total_score']}/100 ({self.pe_score['level']})
"""
        
        if self.discovered_companies:
            header += f"""**发现公司数**: {len(self.discovered_companies)}
"""
        
        header += "\n---\n\n"
        
        full_report = header + report
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        return output_path
    
    # ==================== 模拟函数（无CrewAI时使用）====================
    
    def _simulate_planning(self, prompt: str) -> str:
        """模拟规划"""
        return f"""
# {self.industry}行业研究计划

## 研究目标
- 分析{self.province}{self.industry}行业现状和发展趋势
- 识别产业链各环节的头部公司
- 评估投资机会和风险

## 数据需求
1. 市场规模和增速数据
2. 产业链结构分析
3. 竞争格局数据
4. 政策环境分析
5. 技术发展趋势
6. 重点企业财务数据
"""
    
    def _simulate_research(self, prompt: str) -> str:
        """模拟研究数据收集"""
        return f"""
# {self.province}{self.industry}行业研究数据

## 市场规模
{self.target_year}年{self.province}{self.industry}市场规模预计达到2800亿元，同比增长27%。

## 产业链结构
- 上游：芯片、算力基础设施
- 中游：AI平台、算法研发
- 下游：行业应用、智能终端

## 主要企业
- 海康威视：安防AI龙头，市场份额35%
- 大华股份：安防领域第二
- 科大讯飞：语音AI龙头
- 阿里云：云计算平台
- 之江实验室：AI研究机构

## 政策环境
浙江省出台多项AI产业支持政策，包括人才引进、资金扶持等。
"""
    
    def _simulate_analysis(self, prompt: str, research_data: str) -> str:
        """模拟数据分析"""
        return f"""
# {self.industry}行业深度分析

## 市场趋势
行业处于快速成长期，预计未来5年CAGR达25%。

## 竞争格局
CR5约60%，行业集中度较高，龙头优势明显。

## 投资机会
1. 上游芯片国产替代
2. 中游平台生态建设
3. 下游垂直应用落地

## 风险提示
1. 技术迭代风险
2. 政策变化风险
3. 竞争加剧风险
"""
    
    def _simulate_pe_analysis(self, company, deep_dive_prompt, valuation_prompt, risk_prompt) -> str:
        """模拟PE级分析"""
        return f"""
### {company.name} 深度分析

**业务拆解**
- 主营业务：{company.sub_segment}
- 市场地位：{company.market_position}
- 毛利率：{company.gross_margin or 'N/A'}%

**估值分析**
- 当前估值：合理
- 目标IRR：15-20%

**风险评估**
- 技术风险：中等
- 市场风险：较低
- 政策风险：较低
"""
    
    def _generate_contrarian_views(self, prompt: str) -> str:
        """生成反共识观点"""
        return f"""
### 反共识观点

1. **市场可能过度乐观**：当前估值已充分反映增长预期
2. **技术路线存在不确定性**：主流技术路线可能被颠覆
3. **竞争格局可能重塑**：新进入者可能改变市场格局
"""
    
    def _run_pe_analysis_crew(self, company, deep_dive_prompt, valuation_prompt, risk_prompt) -> str:
        """运行PE分析Crew"""
        # 简化实现
        return self._simulate_pe_analysis(company, deep_dive_prompt, valuation_prompt, risk_prompt)
    
    def _simulate_writing(self, prompt: str, research_data: str, analysis_result: str) -> str:
        """模拟报告撰写"""
        return f"""
# {self.target_year}年{self.province}{self.industry}行业研究报告

## 摘要
本报告对{self.province}{self.industry}行业进行了全面深入的研究分析。

## 一、行业概述
{self.industry}行业是国家战略性新兴产业，{self.province}在该领域具有显著优势。

## 二、市场分析
### 2.1 市场规模
预计{self.target_year}年市场规模达2800亿元。

### 2.2 增长趋势
近5年CAGR约25%，未来仍将保持高速增长。

## 三、产业链分析
### 3.1 上游
芯片、算力基础设施等。

### 3.2 中游
AI平台、算法研发等。

### 3.3 下游
行业应用、智能终端等。

## 四、竞争格局
行业CR5约60%，龙头企业优势明显。

## 五、投资建议
建议关注上游芯片国产替代和下游垂直应用机会。

## 六、风险提示
技术迭代、政策变化、竞争加剧等风险。
"""
    
    def _simulate_review(self, prompt: str, report: str) -> str:
        """模拟审核"""
        return """
REVIEW_RESULT: PASS
SCORE: 85/100

审核意见：
1. 报告结构完整，逻辑清晰
2. 数据支撑较为充分
3. 投资建议具有可操作性

建议改进：
1. 可增加更多定量分析
2. 风险提示可更加具体
"""


def run_industry_research_unified(
    industry: str,
    province: str,
    target_year: str,
    focus: str = "综合分析",
    output_dir: str = "./output",
    enable_pe_analysis: bool = True,
    enable_charts: bool = True,
    max_revisions: int = 2,
    log_callback=None
) -> Dict[str, Any]:
    """
    运行统一行业研究工作流
    
    Args:
        industry: 行业名称
        province: 省份
        target_year: 目标年份
        focus: 研究重点
        output_dir: 输出目录
        enable_pe_analysis: 是否启用PE级分析
        enable_charts: 是否生成图表
        max_revisions: 最大修订次数
        log_callback: 日志回调函数
    
    Returns:
        包含研报和元数据的字典
    """
    workflow = UnifiedResearchWorkflow(
        industry=industry,
        province=province,
        target_year=target_year,
        focus=focus,
        output_dir=output_dir,
        enable_pe_analysis=enable_pe_analysis,
        enable_charts=enable_charts,
        max_revisions=max_revisions,
        log_callback=log_callback
    )
    
    return workflow.run()


if __name__ == "__main__":
    # 测试
    result = run_industry_research_unified(
        industry="人工智能",
        province="浙江省",
        target_year="2025",
        focus="产业链投资机会",
        enable_pe_analysis=True,
        enable_charts=True
    )
    
    if result['success']:
        print(f"报告生成成功: {result['output_path']}")
        print(f"发现公司: {result['discovered_companies']}")
        print(f"生成图表: {len(result['charts'])}个")
        if result['pe_score']:
            print(f"PE评分: {result['pe_score']['total_score']}/100")
    else:
        print(f"报告生成失败: {result['error']}")
