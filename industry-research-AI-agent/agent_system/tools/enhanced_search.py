# agent_system/tools/enhanced_search.py
"""
增强版搜索工具
拆分为专项搜索工具，提高搜索精度

核心改进：
1. 拆分搜索工具 - 财务、政策、市场规模各自独立
2. 多轮搜索 - 自动进行补充搜索
3. 结果验证 - 检查搜索结果质量
4. 来源标注 - 自动标注数据来源
"""

from crewai.tools import BaseTool
from crewai_tools import SerperDevTool
from typing import List, Dict, Optional, Any
import re
import time


# 初始化基础搜索工具
serper_tool = SerperDevTool(n_results=8)


class EnhancedSearchBase(BaseTool):
    """增强搜索基类"""
    
    # 类属性声明
    name: str = "Enhanced Search Base"
    description: str = "Base class for enhanced search tools"
    
    # 搜索配置
    max_retries: int = 2
    retry_delay: float = 1.0
    
    def _safe_search(self, query: str) -> str:
        """安全搜索，带重试机制"""
        for attempt in range(self.max_retries):
            try:
                result = serper_tool.run(query)
                if result and len(result) > 50:
                    return result
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return f"搜索失败: {str(e)}"
        return "未找到相关信息"
    
    def _extract_numbers(self, text: str) -> List[Dict]:
        """从文本中提取数字和单位"""
        patterns = [
            r'([\d,\.]+)\s*(亿|万|%|元|美元|人民币)',
            r'([\d,\.]+)\s*(亿元|万元|百分比)',
            r'CAGR[：:]\s*([\d\.]+)%',
            r'增速[：:]\s*([\d\.]+)%',
        ]
        
        results = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    value = float(match[0].replace(",", ""))
                    unit = match[1] if len(match) > 1 else ""
                    results.append({"value": value, "unit": unit})
                except:
                    continue
        return results
    
    def _format_with_source(self, content: str, source: str) -> str:
        """添加来源标注"""
        return f"{content}\n[数据来源: {source}]"


class FinancialDataSearchTool(EnhancedSearchBase):
    """
    财务数据专项搜索工具
    专注于搜索企业财务指标
    """
    
    name: str = "Financial Data Search"
    description: str = """专门搜索企业财务数据。
输入格式: 公司名称 或 公司名称,年份
示例: "比亚迪" 或 "比亚迪,2024"
返回: 营收、净利润、毛利率、ROE等财务指标"""
    
    def _run(self, query: str) -> str:
        try:
            parts = query.strip().split(",")
            company = parts[0].strip()
            year = parts[1].strip() if len(parts) > 1 else "2024"
            
            # 多维度搜索
            queries = [
                f"{company} {year}年 营收 净利润 财报",
                f"{company} {year} 毛利率 ROE 财务指标",
                f"{company} 年报 {year} 财务数据",
                f"{company} 市值 PE PB 估值"
            ]
            
            all_results = []
            for q in queries:
                result = self._safe_search(q)
                if result and "未找到" not in result:
                    all_results.append(f"【{q}】\n{result}")
            
            if not all_results:
                return f"未找到 {company} 的财务数据"
            
            # 整理输出
            output = f"【{company}】财务数据搜索结果\n"
            output += "=" * 50 + "\n\n"
            output += "\n\n".join(all_results)
            
            # 提取关键数字
            numbers = self._extract_numbers(output)
            if numbers:
                output += "\n\n【提取的关键数据】\n"
                for num in numbers[:10]:
                    output += f"- {num['value']}{num['unit']}\n"
            
            return output
            
        except Exception as e:
            return f"财务数据搜索失败: {str(e)}"


class PolicySearchToolEnhanced(EnhancedSearchBase):
    """
    政策搜索增强工具
    专注于搜索产业政策和监管信息
    """
    
    name: str = "Industry Policy Search Enhanced"
    description: str = """专门搜索行业政策信息。
输入格式: 行业名称 或 行业名称,省份
示例: "人工智能" 或 "人工智能,浙江省"
返回: 国家政策、地方政策、补贴措施、监管要求"""
    
    def _run(self, query: str) -> str:
        try:
            parts = query.strip().split(",")
            industry = parts[0].strip()
            province = parts[1].strip() if len(parts) > 1 else ""
            
            # 构建搜索查询
            queries = [
                f"{industry} 产业政策 国家 十四五",
                f"{industry} 补贴政策 扶持措施 2024 2025",
                f"{industry} 监管政策 行业规范 标准",
            ]
            
            if province:
                queries.extend([
                    f"{province} {industry} 产业政策 规划",
                    f"{province} {industry} 补贴 扶持",
                    f"{province} {industry} 发展目标 十四五"
                ])
            
            all_results = []
            for q in queries:
                result = self._safe_search(q)
                if result and "未找到" not in result:
                    all_results.append(f"【{q}】\n{result}")
            
            if not all_results:
                return f"未找到 {industry} 行业的政策信息"
            
            # 整理输出
            output = f"【{industry}】政策搜索结果"
            if province:
                output += f"（{province}）"
            output += "\n" + "=" * 50 + "\n\n"
            output += "\n\n".join(all_results)
            
            return output
            
        except Exception as e:
            return f"政策搜索失败: {str(e)}"


class MarketSizeSearchToolEnhanced(EnhancedSearchBase):
    """
    市场规模搜索增强工具
    专注于搜索行业市场规模和增长数据
    """
    
    name: str = "Market Size Search Enhanced"
    description: str = """专门搜索行业市场规模数据。
输入格式: 行业名称 或 行业名称,地区
示例: "人工智能" 或 "人工智能,中国"
返回: 市场规模、增速、CAGR、渗透率、预测数据"""
    
    def _run(self, query: str) -> str:
        try:
            parts = query.strip().split(",")
            industry = parts[0].strip()
            region = parts[1].strip() if len(parts) > 1 else "中国"
            
            # 多角度搜索
            queries = [
                f"{region} {industry} 市场规模 2024 2025",
                f"{industry} 市场规模 增速 CAGR",
                f"{industry} 行业规模 预测 2025 2030",
                f"{industry} 渗透率 市场空间 潜力",
                f"{industry} 市场规模 IDC Gartner 艾瑞"  # 权威来源
            ]
            
            all_results = []
            for q in queries:
                result = self._safe_search(q)
                if result and "未找到" not in result:
                    all_results.append(f"【{q}】\n{result}")
            
            if not all_results:
                return f"未找到 {industry} 行业的市场规模数据"
            
            # 整理输出
            output = f"【{industry}】市场规模搜索结果（{region}）\n"
            output += "=" * 50 + "\n\n"
            output += "\n\n".join(all_results)
            
            # 提取关键数字
            numbers = self._extract_numbers(output)
            if numbers:
                output += "\n\n【提取的关键数据】\n"
                for num in numbers[:10]:
                    output += f"- {num['value']}{num['unit']}\n"
            
            return output
            
        except Exception as e:
            return f"市场规模搜索失败: {str(e)}"


class CompetitiveAnalysisSearchTool(EnhancedSearchBase):
    """
    竞争格局搜索工具
    专注于搜索行业竞争格局和龙头企业
    """
    
    name: str = "Competitive Analysis Search"
    description: str = """专门搜索行业竞争格局信息。
输入格式: 行业名称
示例: "人工智能"
返回: 龙头企业、市场份额、CR5/CR10、竞争壁垒"""
    
    def _run(self, query: str) -> str:
        try:
            industry = query.strip()
            
            queries = [
                f"{industry} 龙头企业 TOP10 排名",
                f"{industry} 市场份额 CR5 CR10 集中度",
                f"{industry} 竞争格局 竞争态势 2024",
                f"{industry} 行业壁垒 进入门槛",
                f"{industry} 新进入者 潜在竞争者"
            ]
            
            all_results = []
            for q in queries:
                result = self._safe_search(q)
                if result and "未找到" not in result:
                    all_results.append(f"【{q}】\n{result}")
            
            if not all_results:
                return f"未找到 {industry} 行业的竞争格局信息"
            
            output = f"【{industry}】竞争格局搜索结果\n"
            output += "=" * 50 + "\n\n"
            output += "\n\n".join(all_results)
            
            return output
            
        except Exception as e:
            return f"竞争格局搜索失败: {str(e)}"


class SupplyChainSearchToolEnhanced(EnhancedSearchBase):
    """
    产业链搜索增强工具
    专注于搜索产业链上中下游信息
    """
    
    name: str = "Supply Chain Search Enhanced"
    description: str = """专门搜索产业链信息。
输入格式: 行业名称
示例: "人工智能"
返回: 上游供应商、中游制造商、下游应用、产业链图谱"""
    
    def _run(self, query: str) -> str:
        try:
            industry = query.strip()
            
            # 分层搜索
            queries = [
                f"{industry} 产业链 上游 原材料 供应商",
                f"{industry} 产业链 中游 制造 加工 核心企业",
                f"{industry} 产业链 下游 应用 客户 场景",
                f"{industry} 产业链图谱 全景图 结构",
                f"{industry} 产业链 价值分配 利润分布",
                f"{industry} 产业链 卡脖子 关键环节"
            ]
            
            all_results = []
            for q in queries:
                result = self._safe_search(q)
                if result and "未找到" not in result:
                    all_results.append(f"【{q}】\n{result}")
            
            if not all_results:
                return f"未找到 {industry} 行业的产业链信息"
            
            output = f"【{industry}】产业链搜索结果\n"
            output += "=" * 50 + "\n\n"
            output += "\n\n".join(all_results)
            
            return output
            
        except Exception as e:
            return f"产业链搜索失败: {str(e)}"


class InvestmentSearchTool(EnhancedSearchBase):
    """
    投资信息搜索工具
    专注于搜索投融资和估值信息
    """
    
    name: str = "Investment Information Search"
    description: str = """专门搜索投融资和估值信息。
输入格式: 行业名称 或 公司名称
示例: "人工智能" 或 "商汤科技"
返回: 融资事件、估值水平、投资热点、退出案例"""
    
    def _run(self, query: str) -> str:
        try:
            target = query.strip()
            
            queries = [
                f"{target} 融资 投资 2024 2025",
                f"{target} 估值 PE PS 倍数",
                f"{target} IPO 上市 退出",
                f"{target} 投资热点 趋势 机会",
                f"{target} VC PE 投资案例"
            ]
            
            all_results = []
            for q in queries:
                result = self._safe_search(q)
                if result and "未找到" not in result:
                    all_results.append(f"【{q}】\n{result}")
            
            if not all_results:
                return f"未找到 {target} 的投资信息"
            
            output = f"【{target}】投资信息搜索结果\n"
            output += "=" * 50 + "\n\n"
            output += "\n\n".join(all_results)
            
            return output
            
        except Exception as e:
            return f"投资信息搜索失败: {str(e)}"


class CodeExecutorTool(BaseTool):
    """
    代码执行工具
    让Agent能够执行Python代码进行计算
    """
    
    name: str = "Python Code Executor"
    description: str = """执行Python代码进行数据计算和分析。
支持: 数学计算、统计分析、财务计算（IRR/NPV/CAGR）、数据处理
输入: Python代码字符串
示例: "cagr = ((100/50)**(1/5) - 1) * 100; print(f'CAGR: {cagr:.2f}%')"
注意: 禁止文件操作和网络请求"""
    
    def _run(self, code: str) -> str:
        try:
            from agent_system.tools.code_executor import code_executor
            result = code_executor.execute(code)
            
            if result.success:
                output = f"执行成功:\n{result.output}"
                if result.variables:
                    output += f"\n\n变量结果:\n{result.variables}"
                return output
            else:
                return f"执行失败:\n{result.error}"
                
        except Exception as e:
            return f"代码执行工具错误: {str(e)}"


# 实例化工具
financial_data_search = FinancialDataSearchTool()
policy_search_enhanced = PolicySearchToolEnhanced()
market_size_search_enhanced = MarketSizeSearchToolEnhanced()
competitive_analysis_search = CompetitiveAnalysisSearchTool()
supply_chain_search_enhanced = SupplyChainSearchToolEnhanced()
investment_search = InvestmentSearchTool()
code_executor_tool = CodeExecutorTool()
