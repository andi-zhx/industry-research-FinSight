# memory_system/enhanced_memory.py
"""
增强版Memory模块
集成事实核查、全局上下文共享、智能学习

核心功能：
1. 事实核查 - 写作前检查数据一致性
2. 全局上下文 - 确保所有Agent共享一致数据
3. 智能学习 - 从成功研究中提取经验
4. 知识图谱 - 构建行业关联网络
"""

import datetime
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

# 导入全局上下文管理器
from agent_system.context.global_context import (
    global_context_manager, 
    fact_checker,
    GlobalContext
)


@dataclass
class ResearchSession:
    """研究会话"""
    session_id: str
    industry: str
    province: str
    target_year: str
    focus: str
    start_time: str
    status: str = "active"
    
    # 会话数据
    collected_facts: Dict[str, Any] = field(default_factory=dict)
    agent_outputs: Dict[str, str] = field(default_factory=dict)
    quality_scores: Dict[str, float] = field(default_factory=dict)
    
    # 元数据
    total_searches: int = 0
    total_rag_queries: int = 0
    data_coverage: float = 0.0


class EnhancedMemoryManager:
    """
    增强版记忆管理器
    整合事实核查、上下文共享、智能学习
    """
    
    def __init__(self, base_memory_manager=None):
        """
        初始化增强记忆管理器
        
        Args:
            base_memory_manager: 基础记忆管理器实例
        """
        self.base_manager = base_memory_manager
        self.ctx_manager = global_context_manager
        self.fact_checker = fact_checker
        
        # 当前研究会话
        self.current_session: Optional[ResearchSession] = None
        
        # 会话历史
        self.session_history: List[ResearchSession] = []
        
        # 学习记录
        self.learning_records: List[Dict] = []
    
    def start_session(self, industry: str, province: str, 
                      target_year: str, focus: str) -> ResearchSession:
        """
        开始新的研究会话
        
        Args:
            industry: 行业
            province: 省份
            target_year: 目标年份
            focus: 研究侧重点
        
        Returns:
            ResearchSession: 新的会话对象
        """
        # 生成会话ID
        session_id = hashlib.md5(
            f"{industry}_{province}_{target_year}_{datetime.datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        # 初始化全局上下文
        self.ctx_manager.init_context(industry, province, target_year, focus)
        
        # 创建会话
        self.current_session = ResearchSession(
            session_id=session_id,
            industry=industry,
            province=province,
            target_year=target_year,
            focus=focus,
            start_time=datetime.datetime.now().isoformat()
        )
        
        print(f"🚀 [EnhancedMemory] 开始研究会话: {session_id}")
        print(f"   行业: {industry} | 区域: {province} | 年份: {target_year}")
        
        return self.current_session
    
    def register_fact(self, key: str, value: Any, source: str, 
                      agent: str = "") -> bool:
        """
        注册事实到全局上下文
        
        Args:
            key: 事实标识
            value: 事实值
            source: 数据来源
            agent: 记录的Agent
        
        Returns:
            bool: 是否成功注册
        """
        success = self.ctx_manager.register_fact(key, value, source, agent)
        
        # 同时记录到会话
        if self.current_session:
            self.current_session.collected_facts[key] = {
                "value": value,
                "source": source,
                "agent": agent,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        return success
    
    def check_consistency(self, content: str) -> Dict[str, Any]:
        """
        检查内容的数据一致性
        
        Args:
            content: 待检查的内容
        
        Returns:
            Dict: 检查结果
        """
        return self.fact_checker.check_content(content)
    
    def get_context_prompt(self) -> str:
        """
        获取全局上下文的Prompt格式
        用于注入到Agent提示词中
        """
        return self.ctx_manager.export_context_prompt()
    
    def record_agent_output(self, agent_name: str, output: str, 
                            quality_score: float = None):
        """
        记录Agent输出
        
        Args:
            agent_name: Agent名称
            output: 输出内容
            quality_score: 质量评分
        """
        if self.current_session:
            self.current_session.agent_outputs[agent_name] = output
            if quality_score is not None:
                self.current_session.quality_scores[agent_name] = quality_score
        
        # 从输出中提取事实
        self._extract_and_register_facts(output, agent_name)
    
    def _extract_and_register_facts(self, content: str, agent: str):
        """从内容中提取事实并注册"""
        import re
        
        # 提取市场规模
        market_patterns = [
            r'市场规模[：:约为达到]\s*([\d,\.]+)\s*(亿|万)',
            r'规模[：:约为达到]\s*([\d,\.]+)\s*(亿|万)',
        ]
        for pattern in market_patterns:
            match = re.search(pattern, content)
            if match:
                value = float(match.group(1).replace(",", ""))
                unit = match.group(2)
                self.register_fact(
                    f"市场规模_{self.ctx_manager.context.target_year}",
                    f"{value}{unit}元",
                    f"Agent:{agent}提取"
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
                value = float(match.group(1))
                self.register_fact(
                    "增长率",
                    f"{value}%",
                    f"Agent:{agent}提取"
                )
                break
    
    def get_data_coverage(self) -> Dict[str, Any]:
        """
        获取数据覆盖率报告
        """
        from agent_system.quality.data_quality import data_quality_checker
        
        if not self.current_session:
            return {"error": "无活动会话"}
        
        # 合并所有Agent输出
        combined_content = "\n".join(self.current_session.agent_outputs.values())
        
        # 检查覆盖率
        quality = data_quality_checker.check_coverage(combined_content)
        
        # 更新会话
        self.current_session.data_coverage = quality.total_score
        
        return {
            "total_score": quality.total_score,
            "dimension_scores": quality.dimension_scores,
            "missing_data": quality.missing_data,
            "pass_threshold": quality.pass_threshold,
            "recommendations": quality.recommendations
        }
    
    def end_session(self, final_report: str = None, 
                    quality_score: float = None) -> Dict[str, Any]:
        """
        结束研究会话
        
        Args:
            final_report: 最终报告
            quality_score: 最终质量评分
        
        Returns:
            Dict: 会话总结
        """
        if not self.current_session:
            return {"error": "无活动会话"}
        
        self.current_session.status = "completed"
        
        # 计算会话统计
        summary = {
            "session_id": self.current_session.session_id,
            "industry": self.current_session.industry,
            "province": self.current_session.province,
            "duration": self._calculate_duration(),
            "facts_collected": len(self.current_session.collected_facts),
            "agents_involved": list(self.current_session.agent_outputs.keys()),
            "data_coverage": self.current_session.data_coverage,
            "quality_score": quality_score,
            "conflicts": len(self.ctx_manager.get_conflicts())
        }
        
        # 学习经验
        if quality_score and quality_score >= 0.8:
            self._learn_from_success()
        
        # 保存到历史
        self.session_history.append(self.current_session)
        
        # 保存最终报告到基础记忆
        if final_report and self.base_manager:
            self.base_manager.save_insight(
                content=final_report,
                category="report_segment",
                metadata={
                    "industry": self.current_session.industry,
                    "province": self.current_session.province,
                    "year": self.current_session.target_year,
                    "session_id": self.current_session.session_id,
                    "quality_score": quality_score
                }
            )
        
        print(f"✅ [EnhancedMemory] 会话结束: {self.current_session.session_id}")
        print(f"   收集事实: {summary['facts_collected']} | 数据覆盖率: {summary['data_coverage']:.1%}")
        
        self.current_session = None
        
        return summary
    
    def _calculate_duration(self) -> str:
        """计算会话持续时间"""
        if not self.current_session:
            return "0分钟"
        
        start = datetime.datetime.fromisoformat(self.current_session.start_time)
        duration = datetime.datetime.now() - start
        minutes = int(duration.total_seconds() / 60)
        
        if minutes < 60:
            return f"{minutes}分钟"
        else:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}小时{mins}分钟"
    
    def _learn_from_success(self):
        """从成功的研究中学习"""
        if not self.current_session:
            return
        
        # 提取成功模式
        pattern = {
            "industry": self.current_session.industry,
            "province": self.current_session.province,
            "facts_count": len(self.current_session.collected_facts),
            "agents_used": list(self.current_session.agent_outputs.keys()),
            "key_facts": list(self.current_session.collected_facts.keys())[:10],
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        self.learning_records.append(pattern)
        
        # 保存到基础记忆
        if self.base_manager:
            self.base_manager.save_research_experience(
                industry=self.current_session.industry,
                dimension="综合",
                insight=f"成功完成{self.current_session.industry}行业研究，收集{len(self.current_session.collected_facts)}个关键事实",
                success=True
            )
        
        print(f"📚 [EnhancedMemory] 学习成功模式: {self.current_session.industry}")
    
    def get_similar_research(self, industry: str, k: int = 3) -> List[Dict]:
        """
        获取相似的历史研究
        
        Args:
            industry: 行业
            k: 返回数量
        
        Returns:
            List[Dict]: 相似研究列表
        """
        similar = []
        
        # 从会话历史中查找
        for session in reversed(self.session_history):
            if session.industry == industry and session.status == "completed":
                similar.append({
                    "session_id": session.session_id,
                    "province": session.province,
                    "target_year": session.target_year,
                    "data_coverage": session.data_coverage,
                    "facts_count": len(session.collected_facts)
                })
                if len(similar) >= k:
                    break
        
        # 从基础记忆中补充
        if self.base_manager and len(similar) < k:
            base_results = self.base_manager.recall_similar_reports(industry, k=k-len(similar))
            for result in base_results:
                similar.append({
                    "content_preview": result.get("content", "")[:200],
                    "metadata": result.get("metadata", {})
                })
        
        return similar
    
    def export_session_data(self, output_path: str):
        """导出会话数据"""
        if not self.current_session:
            print("⚠️ 无活动会话")
            return
        
        data = {
            "session_id": self.current_session.session_id,
            "industry": self.current_session.industry,
            "province": self.current_session.province,
            "target_year": self.current_session.target_year,
            "focus": self.current_session.focus,
            "start_time": self.current_session.start_time,
            "collected_facts": self.current_session.collected_facts,
            "quality_scores": self.current_session.quality_scores,
            "global_facts": self.ctx_manager.get_all_facts(),
            "conflicts": self.ctx_manager.get_conflicts()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📤 [EnhancedMemory] 会话数据已导出: {output_path}")


class FactValidationMiddleware:
    """
    事实验证中间件
    在Agent输出前进行事实核查
    """
    
    def __init__(self, memory_manager: EnhancedMemoryManager):
        self.memory = memory_manager
    
    def validate_before_write(self, content: str, agent_name: str) -> Tuple[bool, str, List[str]]:
        """
        写作前验证
        
        Args:
            content: 待验证内容
            agent_name: Agent名称
        
        Returns:
            Tuple[bool, str, List[str]]: (是否通过, 修正后内容, 问题列表)
        """
        # 检查一致性
        check_result = self.memory.check_consistency(content)
        
        issues = []
        corrected_content = content
        
        if not check_result["passed"]:
            for issue in check_result["issues"]:
                issues.append(
                    f"数据不一致: {issue['fact_key']} 期望值={issue['expected']}, 发现值={issue['found']}"
                )
                
                # 尝试自动修正
                try:
                    corrected_content = corrected_content.replace(
                        str(issue['found']),
                        str(issue['expected'])
                    )
                except:
                    pass
        
        return check_result["passed"], corrected_content, issues
    
    def validate_after_research(self, research_output: str) -> Dict[str, Any]:
        """
        研究后验证
        
        Args:
            research_output: 研究输出
        
        Returns:
            Dict: 验证结果
        """
        # 获取数据覆盖率
        coverage = self.memory.get_data_coverage()
        
        # 检查一致性
        consistency = self.memory.check_consistency(research_output)
        
        return {
            "data_coverage": coverage,
            "consistency_check": consistency,
            "overall_passed": coverage.get("pass_threshold", False) and consistency.get("passed", False)
        }


# 全局实例
try:
    from memory_system.memory_manager import memory_manager as base_memory
    enhanced_memory = EnhancedMemoryManager(base_memory)
except ImportError:
    enhanced_memory = EnhancedMemoryManager(None)

fact_validation = FactValidationMiddleware(enhanced_memory)
