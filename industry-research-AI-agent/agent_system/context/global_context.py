# agent_system/context/global_context.py
"""
全局上下文管理器
确保所有Agent共享一致的核心数据和元信息

核心功能：
1. 全局变量共享池 - 核心指标在所有Agent间透传
2. 事实一致性校验 - 防止前后矛盾
3. 数据版本控制 - 追踪数据变更
"""

import datetime
import hashlib
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from threading import Lock
from collections import defaultdict


@dataclass
class FactRecord:
    """事实记录"""
    key: str  # 事实标识（如：市场规模_2025）
    value: Any  # 事实值
    source: str  # 数据来源
    timestamp: str  # 记录时间
    confidence: float = 1.0  # 置信度
    agent: str = ""  # 记录的Agent
    version: int = 1  # 版本号


@dataclass
class GlobalContext:
    """
    全局上下文对象
    在所有Agent间共享的核心数据
    """
    # 研究元数据
    industry: str = ""
    province: str = ""
    target_year: str = ""
    focus: str = ""
    report_date: str = ""
    
    # 核心指标（必须保持一致）
    market_size: Optional[float] = None  # 市场规模（亿元）
    market_size_unit: str = "亿元"
    growth_rate: Optional[float] = None  # 增长率（%）
    cagr: Optional[float] = None  # 复合增长率（%）
    
    # 关键企业列表
    key_companies: List[str] = field(default_factory=list)
    
    # 产业链结构
    upstream_players: List[str] = field(default_factory=list)
    midstream_players: List[str] = field(default_factory=list)
    downstream_players: List[str] = field(default_factory=list)
    
    # 政策关键词
    key_policies: List[str] = field(default_factory=list)
    
    # 自定义数据
    custom_data: Dict[str, Any] = field(default_factory=dict)


class GlobalContextManager:
    """
    全局上下文管理器
    单例模式，确保全局唯一
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.context = GlobalContext()
        self.facts: Dict[str, FactRecord] = {}  # 事实库
        self.fact_history: List[FactRecord] = []  # 事实变更历史
        self.conflicts: List[Dict] = []  # 冲突记录
        self._fact_lock = Lock()
    
    def init_context(self, industry: str, province: str, 
                     target_year: str, focus: str) -> GlobalContext:
        """
        初始化研究上下文
        
        Args:
            industry: 行业
            province: 省份
            target_year: 目标年份
            focus: 研究侧重点
        
        Returns:
            GlobalContext: 初始化后的上下文
        """
        self.context = GlobalContext(
            industry=industry,
            province=province,
            target_year=target_year,
            focus=focus,
            report_date=datetime.datetime.now().strftime("%Y年%m月%d日")
        )
        
        # 清空事实库
        self.facts.clear()
        self.fact_history.clear()
        self.conflicts.clear()
        
        print(f"🌐 [GlobalContext] 已初始化: {industry} | {province} | {target_year}")
        
        return self.context
    
    def register_fact(self, key: str, value: Any, source: str, 
                      agent: str = "", confidence: float = 1.0) -> bool:
        """
        注册事实
        如果已存在相同key的事实，进行一致性检查
        
        Args:
            key: 事实标识
            value: 事实值
            source: 数据来源
            agent: 记录的Agent
            confidence: 置信度
        
        Returns:
            bool: 是否成功注册（无冲突）
        """
        with self._fact_lock:
            fact_key = self._normalize_key(key)
            
            # 检查是否已存在
            if fact_key in self.facts:
                existing = self.facts[fact_key]
                
                # 检查一致性
                if not self._is_consistent(existing.value, value):
                    # 记录冲突
                    conflict = {
                        "key": fact_key,
                        "existing_value": existing.value,
                        "existing_source": existing.source,
                        "new_value": value,
                        "new_source": source,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    self.conflicts.append(conflict)
                    
                    print(f"⚠️ [GlobalContext] 数据冲突: {fact_key}")
                    print(f"   已有值: {existing.value} (来源: {existing.source})")
                    print(f"   新值: {value} (来源: {source})")
                    
                    # 根据置信度决定是否更新
                    if confidence > existing.confidence:
                        self._update_fact(fact_key, value, source, agent, confidence)
                        return True
                    return False
                else:
                    # 一致，更新版本
                    existing.version += 1
                    existing.timestamp = datetime.datetime.now().isoformat()
                    return True
            
            # 新增事实
            fact = FactRecord(
                key=fact_key,
                value=value,
                source=source,
                timestamp=datetime.datetime.now().isoformat(),
                confidence=confidence,
                agent=agent,
                version=1
            )
            self.facts[fact_key] = fact
            self.fact_history.append(fact)
            
            print(f"📝 [GlobalContext] 注册事实: {fact_key} = {value}")
            
            return True
    
    def get_fact(self, key: str) -> Optional[Any]:
        """获取事实值"""
        fact_key = self._normalize_key(key)
        fact = self.facts.get(fact_key)
        return fact.value if fact else None
    
    def get_fact_with_source(self, key: str) -> Optional[FactRecord]:
        """获取事实记录（含来源）"""
        fact_key = self._normalize_key(key)
        return self.facts.get(fact_key)
    
    def check_consistency(self, key: str, value: Any) -> bool:
        """
        检查值是否与已注册的事实一致
        
        Args:
            key: 事实标识
            value: 待检查的值
        
        Returns:
            bool: 是否一致
        """
        fact_key = self._normalize_key(key)
        if fact_key not in self.facts:
            return True  # 不存在则视为一致
        
        return self._is_consistent(self.facts[fact_key].value, value)
    
    def get_all_facts(self) -> Dict[str, Any]:
        """获取所有事实"""
        return {k: v.value for k, v in self.facts.items()}
    
    def get_conflicts(self) -> List[Dict]:
        """获取所有冲突记录"""
        return self.conflicts.copy()
    
    def export_context_prompt(self) -> str:
        """
        导出上下文为Prompt格式
        用于注入到Agent的提示词中
        """
        ctx = self.context
        
        prompt = f"""
【全局上下文 - 必须保持一致】
研究行业: {ctx.industry}
研究区域: {ctx.province}
目标年份: {ctx.target_year}
研究侧重: {ctx.focus}
报告日期: {ctx.report_date}
"""
        
        # 添加核心指标
        if ctx.market_size is not None:
            prompt += f"\n市场规模: {ctx.market_size}{ctx.market_size_unit}"
        if ctx.growth_rate is not None:
            prompt += f"\n增长率: {ctx.growth_rate}%"
        if ctx.cagr is not None:
            prompt += f"\nCAGR: {ctx.cagr}%"
        
        # 添加关键企业
        if ctx.key_companies:
            prompt += f"\n关键企业: {', '.join(ctx.key_companies[:10])}"
        
        # 添加已注册的事实
        if self.facts:
            prompt += "\n\n【已确认的事实数据 - 引用时必须保持一致】"
            for key, fact in list(self.facts.items())[:20]:  # 限制数量
                prompt += f"\n- {key}: {fact.value} [来源: {fact.source}]"
        
        return prompt
    
    def _normalize_key(self, key: str) -> str:
        """标准化事实key"""
        # 去除空格，转小写，统一格式
        return key.strip().lower().replace(" ", "_").replace("：", "_").replace(":", "_")
    
    def _is_consistent(self, value1: Any, value2: Any) -> bool:
        """
        检查两个值是否一致
        支持数值的近似比较
        """
        # 类型不同
        if type(value1) != type(value2):
            # 尝试转换比较
            try:
                v1 = float(str(value1).replace(",", "").replace("亿", "").replace("万", ""))
                v2 = float(str(value2).replace(",", "").replace("亿", "").replace("万", ""))
                # 允许5%的误差
                return abs(v1 - v2) / max(v1, v2, 1) < 0.05
            except:
                return str(value1) == str(value2)
        
        # 数值比较
        if isinstance(value1, (int, float)):
            if value1 == 0 and value2 == 0:
                return True
            # 允许5%的误差
            return abs(value1 - value2) / max(abs(value1), abs(value2), 1) < 0.05
        
        # 字符串比较
        return str(value1).strip() == str(value2).strip()
    
    def _update_fact(self, key: str, value: Any, source: str, 
                     agent: str, confidence: float):
        """更新事实"""
        old_fact = self.facts[key]
        new_fact = FactRecord(
            key=key,
            value=value,
            source=source,
            timestamp=datetime.datetime.now().isoformat(),
            confidence=confidence,
            agent=agent,
            version=old_fact.version + 1
        )
        self.facts[key] = new_fact
        self.fact_history.append(new_fact)
        
        print(f"🔄 [GlobalContext] 更新事实: {key} = {value} (v{new_fact.version})")


class FactChecker:
    """
    事实核查器
    在写作前检查数据一致性
    """
    
    def __init__(self, context_manager: GlobalContextManager):
        self.ctx_manager = context_manager
    
    def check_content(self, content: str) -> Dict[str, Any]:
        """
        检查内容中的数据是否与全局上下文一致
        
        Args:
            content: 待检查的内容
        
        Returns:
            Dict: 检查结果
        """
        issues = []
        warnings = []
        
        # 提取内容中的数字
        numbers = self._extract_numbers(content)
        
        # 与已注册的事实对比
        for key, fact in self.ctx_manager.facts.items():
            if isinstance(fact.value, (int, float)):
                # 检查内容中是否有不一致的数字
                for num_info in numbers:
                    if self._is_related(key, num_info["context"]):
                        if not self.ctx_manager._is_consistent(fact.value, num_info["value"]):
                            issues.append({
                                "type": "inconsistency",
                                "fact_key": key,
                                "expected": fact.value,
                                "found": num_info["value"],
                                "context": num_info["context"]
                            })
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "checked_facts": len(self.ctx_manager.facts)
        }
    
    def _extract_numbers(self, content: str) -> List[Dict]:
        """从内容中提取数字及其上下文"""
        import re
        
        results = []
        # 匹配数字（包括带单位的）
        pattern = r'([\d,\.]+)\s*(亿|万|%|元|美元)?'
        
        for match in re.finditer(pattern, content):
            try:
                value = float(match.group(1).replace(",", ""))
                unit = match.group(2) or ""
                
                # 获取上下文（前后各20个字符）
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 20)
                context = content[start:end]
                
                results.append({
                    "value": value,
                    "unit": unit,
                    "context": context
                })
            except:
                continue
        
        return results
    
    def _is_related(self, fact_key: str, context: str) -> bool:
        """判断上下文是否与事实相关"""
        # 简单的关键词匹配
        keywords = fact_key.replace("_", " ").split()
        context_lower = context.lower()
        
        return any(kw.lower() in context_lower for kw in keywords)


# 全局实例
global_context_manager = GlobalContextManager()
fact_checker = FactChecker(global_context_manager)
