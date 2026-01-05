# agent_system/discovery/company_discovery.py
"""
自动公司发现模块
在产业链分析过程中自动识别各环节的头部公司
并进行PE级深度分析
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import re


@dataclass
class DiscoveredCompany:
    """发现的公司信息"""
    name: str
    segment: str  # 产业链环节：上游/中游/下游
    sub_segment: str  # 细分环节
    market_position: str  # 市场地位：龙头/头部/中等/新锐
    market_share: Optional[float] = None  # 市场份额
    revenue: Optional[float] = None  # 营收（亿元）
    gross_margin: Optional[float] = None  # 毛利率
    is_listed: bool = False  # 是否上市
    stock_code: Optional[str] = None  # 股票代码
    core_products: List[str] = field(default_factory=list)  # 核心产品
    competitive_advantages: List[str] = field(default_factory=list)  # 竞争优势
    data_source: str = ""  # 数据来源
    confidence: float = 0.0  # 置信度 0-1


@dataclass
class SupplyChainMap:
    """产业链图谱"""
    industry: str
    province: str
    upstream: List[Dict] = field(default_factory=list)  # 上游环节
    midstream: List[Dict] = field(default_factory=list)  # 中游环节
    downstream: List[Dict] = field(default_factory=list)  # 下游环节
    key_companies: List[DiscoveredCompany] = field(default_factory=list)
    value_distribution: Dict[str, float] = field(default_factory=dict)  # 价值分配


class CompanyDiscoveryEngine:
    """
    公司发现引擎
    自动从研究数据中识别产业链各环节的头部公司
    """
    
    # 产业链关键词映射
    SEGMENT_KEYWORDS = {
        '上游': ['原材料', '零部件', '供应商', '芯片', '设备', '基础设施', '算力', '数据'],
        '中游': ['制造', '加工', '平台', '系统', '解决方案', '集成', '研发', '技术'],
        '下游': ['应用', '终端', '服务', '客户', '场景', '消费', '行业应用', '落地']
    }
    
    # 市场地位关键词
    POSITION_KEYWORDS = {
        '龙头': ['龙头', '领军', '第一', '最大', '领先', '头部', 'TOP1', '冠军'],
        '头部': ['头部', '前三', '前五', 'TOP3', 'TOP5', '主要', '重要'],
        '中等': ['中等', '中型', '区域', '细分'],
        '新锐': ['新锐', '新兴', '独角兽', '高成长', '创新']
    }
    
    def __init__(self, llm_client=None):
        """
        初始化公司发现引擎
        
        Args:
            llm_client: LLM客户端（用于智能提取）
        """
        self.llm_client = llm_client
        self.discovered_companies: List[DiscoveredCompany] = []
        self.supply_chain_map: Optional[SupplyChainMap] = None
    
    def discover_from_research_data(
        self,
        research_data: str,
        industry: str,
        province: str
    ) -> List[DiscoveredCompany]:
        """
        从研究数据中发现公司
        
        Args:
            research_data: 研究数据文本
            industry: 行业
            province: 省份
        
        Returns:
            发现的公司列表
        """
        companies = []
        
        # 1. 使用规则提取公司
        rule_companies = self._extract_by_rules(research_data, industry)
        companies.extend(rule_companies)
        
        # 2. 如果有LLM，使用智能提取
        if self.llm_client:
            llm_companies = self._extract_by_llm(research_data, industry, province)
            companies.extend(llm_companies)
        
        # 3. 去重和排序
        companies = self._deduplicate_and_rank(companies)
        
        # 4. 保存结果
        self.discovered_companies = companies
        
        return companies
    
    def _extract_by_rules(self, text: str, industry: str) -> List[DiscoveredCompany]:
        """
        使用规则提取公司
        """
        companies = []
        
        # 常见公司名称模式
        company_patterns = [
            r'([^\s,，、;；]+(?:股份|集团|科技|技术|电子|智能|信息|软件|网络|云|数据|芯片)(?:有限)?(?:公司)?)',
            r'([^\s,，、;；]+(?:控股|投资|资本|基金))',
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',  # 英文公司名
        ]
        
        # 提取公司名称
        found_names = set()
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) >= 2 and len(match) <= 20:
                    found_names.add(match)
        
        # 分析每个公司
        for name in found_names:
            company = self._analyze_company_context(name, text, industry)
            if company:
                companies.append(company)
        
        return companies
    
    def _analyze_company_context(
        self,
        company_name: str,
        text: str,
        industry: str
    ) -> Optional[DiscoveredCompany]:
        """
        分析公司在文本中的上下文，提取信息
        """
        # 查找公司相关的上下文
        context_pattern = rf'.{{0,200}}{re.escape(company_name)}.{{0,200}}'
        contexts = re.findall(context_pattern, text, re.DOTALL)
        
        if not contexts:
            return None
        
        context = ' '.join(contexts)
        
        # 判断产业链环节
        segment = self._determine_segment(context)
        
        # 判断市场地位
        position = self._determine_position(context)
        
        # 提取市场份额
        market_share = self._extract_market_share(context)
        
        # 提取营收
        revenue = self._extract_revenue(context)
        
        # 提取毛利率
        gross_margin = self._extract_gross_margin(context)
        
        # 判断是否上市
        is_listed, stock_code = self._check_listed_status(context, company_name)
        
        # 计算置信度
        confidence = self._calculate_confidence(context, company_name)
        
        if confidence < 0.3:
            return None
        
        return DiscoveredCompany(
            name=company_name,
            segment=segment,
            sub_segment=self._extract_sub_segment(context),
            market_position=position,
            market_share=market_share,
            revenue=revenue,
            gross_margin=gross_margin,
            is_listed=is_listed,
            stock_code=stock_code,
            core_products=self._extract_products(context),
            competitive_advantages=self._extract_advantages(context),
            data_source="规则提取",
            confidence=confidence
        )
    
    def _determine_segment(self, context: str) -> str:
        """判断产业链环节"""
        scores = {'上游': 0, '中游': 0, '下游': 0}
        
        for segment, keywords in self.SEGMENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in context:
                    scores[segment] += 1
        
        max_segment = max(scores, key=scores.get)
        return max_segment if scores[max_segment] > 0 else '中游'
    
    def _determine_position(self, context: str) -> str:
        """判断市场地位"""
        for position, keywords in self.POSITION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in context:
                    return position
        return '中等'
    
    def _extract_market_share(self, context: str) -> Optional[float]:
        """提取市场份额"""
        patterns = [
            r'市场份额[约为是]?(\d+(?:\.\d+)?)[%％]',
            r'占[据有]?[市场]?(\d+(?:\.\d+)?)[%％]',
            r'(\d+(?:\.\d+)?)[%％]的?市场份额',
            r'CR\d+[=为是]?(\d+(?:\.\d+)?)[%％]?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        return None
    
    def _extract_revenue(self, context: str) -> Optional[float]:
        """提取营收"""
        patterns = [
            r'营[业收]?收入?[约为是]?(\d+(?:\.\d+)?)[亿万]',
            r'营收[约为是]?(\d+(?:\.\d+)?)[亿万]',
            r'收入[约为是]?(\d+(?:\.\d+)?)[亿万]',
            r'(\d+(?:\.\d+)?)[亿万]元?[的]?营收',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context)
            if match:
                try:
                    value = float(match.group(1))
                    # 如果是万，转换为亿
                    if '万' in context[match.start():match.end()+5]:
                        value = value / 10000
                    return value
                except:
                    pass
        return None
    
    def _extract_gross_margin(self, context: str) -> Optional[float]:
        """提取毛利率"""
        patterns = [
            r'毛利率[约为是]?(\d+(?:\.\d+)?)[%％]',
            r'(\d+(?:\.\d+)?)[%％]的?毛利率',
            r'毛利[约为是]?(\d+(?:\.\d+)?)[%％]',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        return None
    
    def _check_listed_status(self, context: str, company_name: str) -> tuple:
        """检查上市状态"""
        # 股票代码模式
        stock_patterns = [
            r'[（(](\d{6})[）)]',
            r'股票代码[：:]?(\d{6})',
            r'(\d{6})\.[SZ][HZ]',
        ]
        
        for pattern in stock_patterns:
            match = re.search(pattern, context)
            if match:
                return True, match.group(1)
        
        # 上市关键词
        if any(kw in context for kw in ['上市', 'IPO', 'A股', '港股', '美股', '科创板', '创业板']):
            return True, None
        
        return False, None
    
    def _extract_sub_segment(self, context: str) -> str:
        """提取细分环节"""
        sub_segments = [
            '芯片', '算力', '数据', '平台', '应用', '服务',
            '设备', '材料', '软件', '硬件', '系统', '解决方案'
        ]
        
        for sub in sub_segments:
            if sub in context:
                return sub
        return '综合'
    
    def _extract_products(self, context: str) -> List[str]:
        """提取核心产品"""
        products = []
        
        # 产品关键词模式
        patterns = [
            r'主要产品[包括有：:]+([^。]+)',
            r'核心产品[包括有：:]+([^。]+)',
            r'产品[包括有：:]+([^。]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context)
            if match:
                product_text = match.group(1)
                # 分割产品
                products = [p.strip() for p in re.split(r'[,，、;；]', product_text) if p.strip()]
                break
        
        return products[:5]  # 最多5个产品
    
    def _extract_advantages(self, context: str) -> List[str]:
        """提取竞争优势"""
        advantages = []
        
        advantage_keywords = [
            '技术领先', '成本优势', '规模优势', '品牌优势', '渠道优势',
            '专利', '研发', '客户资源', '产能', '供应链'
        ]
        
        for keyword in advantage_keywords:
            if keyword in context:
                advantages.append(keyword)
        
        return advantages[:5]
    
    def _calculate_confidence(self, context: str, company_name: str) -> float:
        """计算置信度"""
        score = 0.0
        
        # 公司名称出现次数
        count = context.count(company_name)
        score += min(count * 0.1, 0.3)
        
        # 有数据支撑
        if re.search(r'\d+[%％亿万]', context):
            score += 0.2
        
        # 有市场地位描述
        for keywords in self.POSITION_KEYWORDS.values():
            if any(kw in context for kw in keywords):
                score += 0.2
                break
        
        # 有产业链位置描述
        for keywords in self.SEGMENT_KEYWORDS.values():
            if any(kw in context for kw in keywords):
                score += 0.2
                break
        
        # 有具体产品描述
        if any(kw in context for kw in ['产品', '服务', '解决方案', '平台']):
            score += 0.1
        
        return min(score, 1.0)
    
    def _extract_by_llm(
        self,
        text: str,
        industry: str,
        province: str
    ) -> List[DiscoveredCompany]:
        """
        使用LLM智能提取公司
        """
        if not self.llm_client:
            return []
        
        prompt = f"""
请从以下{industry}行业研究文本中提取产业链各环节的头部公司信息。

文本内容：
{text[:5000]}  # 限制长度

请按以下JSON格式输出：
{{
    "companies": [
        {{
            "name": "公司名称",
            "segment": "上游/中游/下游",
            "sub_segment": "细分环节",
            "market_position": "龙头/头部/中等/新锐",
            "market_share": 数字或null,
            "revenue": 数字或null（亿元）,
            "gross_margin": 数字或null（%）,
            "is_listed": true/false,
            "stock_code": "股票代码或null",
            "core_products": ["产品1", "产品2"],
            "competitive_advantages": ["优势1", "优势2"]
        }}
    ]
}}

只输出JSON，不要其他内容。
"""
        
        try:
            response = self.llm_client.generate(prompt)
            data = json.loads(response)
            
            companies = []
            for item in data.get('companies', []):
                company = DiscoveredCompany(
                    name=item.get('name', ''),
                    segment=item.get('segment', '中游'),
                    sub_segment=item.get('sub_segment', ''),
                    market_position=item.get('market_position', '中等'),
                    market_share=item.get('market_share'),
                    revenue=item.get('revenue'),
                    gross_margin=item.get('gross_margin'),
                    is_listed=item.get('is_listed', False),
                    stock_code=item.get('stock_code'),
                    core_products=item.get('core_products', []),
                    competitive_advantages=item.get('competitive_advantages', []),
                    data_source="LLM提取",
                    confidence=0.7
                )
                companies.append(company)
            
            return companies
        except Exception as e:
            print(f"LLM提取失败: {e}")
            return []
    
    def _deduplicate_and_rank(self, companies: List[DiscoveredCompany]) -> List[DiscoveredCompany]:
        """
        去重和排序
        """
        # 按公司名称去重，保留置信度最高的
        company_dict = {}
        for company in companies:
            name = company.name
            if name not in company_dict or company.confidence > company_dict[name].confidence:
                company_dict[name] = company
        
        # 排序：先按产业链位置，再按市场地位，最后按置信度
        segment_order = {'上游': 0, '中游': 1, '下游': 2}
        position_order = {'龙头': 0, '头部': 1, '中等': 2, '新锐': 3}
        
        sorted_companies = sorted(
            company_dict.values(),
            key=lambda c: (
                segment_order.get(c.segment, 1),
                position_order.get(c.market_position, 2),
                -c.confidence
            )
        )
        
        return sorted_companies
    
    def get_top_companies_by_segment(self, segment: str, top_n: int = 3) -> List[DiscoveredCompany]:
        """
        获取指定产业链环节的头部公司
        
        Args:
            segment: 产业链环节（上游/中游/下游）
            top_n: 返回数量
        
        Returns:
            头部公司列表
        """
        segment_companies = [c for c in self.discovered_companies if c.segment == segment]
        
        # 按市场地位和置信度排序
        position_order = {'龙头': 0, '头部': 1, '中等': 2, '新锐': 3}
        sorted_companies = sorted(
            segment_companies,
            key=lambda c: (position_order.get(c.market_position, 2), -c.confidence)
        )
        
        return sorted_companies[:top_n]
    
    def get_key_companies_for_deep_dive(self, max_companies: int = 5) -> List[DiscoveredCompany]:
        """
        获取需要深度分析的关键公司
        
        Args:
            max_companies: 最大公司数量
        
        Returns:
            关键公司列表
        """
        # 优先选择：龙头 > 头部 > 上市公司 > 高置信度
        key_companies = []
        
        # 1. 先选龙头企业
        for company in self.discovered_companies:
            if company.market_position == '龙头' and len(key_companies) < max_companies:
                key_companies.append(company)
        
        # 2. 再选头部企业
        for company in self.discovered_companies:
            if company.market_position == '头部' and company not in key_companies:
                if len(key_companies) < max_companies:
                    key_companies.append(company)
        
        # 3. 选上市公司
        for company in self.discovered_companies:
            if company.is_listed and company not in key_companies:
                if len(key_companies) < max_companies:
                    key_companies.append(company)
        
        # 4. 按置信度补充
        remaining = [c for c in self.discovered_companies if c not in key_companies]
        remaining.sort(key=lambda c: -c.confidence)
        
        for company in remaining:
            if len(key_companies) < max_companies:
                key_companies.append(company)
        
        return key_companies
    
    def build_supply_chain_map(self, industry: str, province: str) -> SupplyChainMap:
        """
        构建产业链图谱
        
        Args:
            industry: 行业
            province: 省份
        
        Returns:
            产业链图谱
        """
        supply_chain = SupplyChainMap(
            industry=industry,
            province=province,
            key_companies=self.discovered_companies
        )
        
        # 按环节分组
        for company in self.discovered_companies:
            company_info = {
                'name': company.name,
                'sub_segment': company.sub_segment,
                'market_position': company.market_position,
                'market_share': company.market_share,
                'revenue': company.revenue,
                'gross_margin': company.gross_margin
            }
            
            if company.segment == '上游':
                supply_chain.upstream.append(company_info)
            elif company.segment == '中游':
                supply_chain.midstream.append(company_info)
            else:
                supply_chain.downstream.append(company_info)
        
        # 计算价值分配
        supply_chain.value_distribution = self._calculate_value_distribution()
        
        self.supply_chain_map = supply_chain
        return supply_chain
    
    def _calculate_value_distribution(self) -> Dict[str, float]:
        """
        计算产业链价值分配
        """
        distribution = {'上游': 0, '中游': 0, '下游': 0}
        
        # 基于毛利率估算
        for segment in ['上游', '中游', '下游']:
            companies = [c for c in self.discovered_companies if c.segment == segment]
            if companies:
                margins = [c.gross_margin for c in companies if c.gross_margin]
                if margins:
                    distribution[segment] = sum(margins) / len(margins)
        
        # 归一化
        total = sum(distribution.values())
        if total > 0:
            for key in distribution:
                distribution[key] = round(distribution[key] / total * 100, 1)
        
        return distribution
    
    def generate_discovery_report(self) -> str:
        """
        生成公司发现报告
        
        Returns:
            Markdown格式的报告
        """
        report = []
        report.append("## 产业链公司发现报告\n")
        report.append(f"发现时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        report.append(f"发现公司总数：{len(self.discovered_companies)}\n\n")
        
        # 按产业链环节分组
        for segment in ['上游', '中游', '下游']:
            companies = [c for c in self.discovered_companies if c.segment == segment]
            if not companies:
                continue
            
            report.append(f"### {segment}产业链\n")
            report.append(f"发现公司数：{len(companies)}\n\n")
            
            # 表格
            report.append("| 公司名称 | 细分环节 | 市场地位 | 市场份额 | 营收(亿) | 毛利率 | 上市 |")
            report.append("|---------|---------|---------|---------|---------|--------|------|")
            
            for c in companies:
                share = f"{c.market_share:.1f}%" if c.market_share else "-"
                revenue = f"{c.revenue:.1f}" if c.revenue else "-"
                margin = f"{c.gross_margin:.1f}%" if c.gross_margin else "-"
                listed = "是" if c.is_listed else "否"
                
                report.append(f"| {c.name} | {c.sub_segment} | {c.market_position} | {share} | {revenue} | {margin} | {listed} |")
            
            report.append("\n")
        
        # 关键公司
        key_companies = self.get_key_companies_for_deep_dive()
        if key_companies:
            report.append("### 建议深度分析的关键公司\n")
            for i, c in enumerate(key_companies, 1):
                report.append(f"{i}. **{c.name}**（{c.segment}-{c.sub_segment}）")
                report.append(f"   - 市场地位：{c.market_position}")
                if c.competitive_advantages:
                    report.append(f"   - 竞争优势：{', '.join(c.competitive_advantages)}")
                report.append("")
        
        return '\n'.join(report)


# 便捷函数
def discover_companies(
    research_data: str,
    industry: str,
    province: str,
    llm_client=None
) -> List[DiscoveredCompany]:
    """
    便捷函数：发现公司
    """
    engine = CompanyDiscoveryEngine(llm_client=llm_client)
    return engine.discover_from_research_data(research_data, industry, province)


def get_prompt_for_company_discovery(industry: str, province: str) -> str:
    """
    获取公司发现的Prompt
    用于在Researcher阶段搜索产业链公司
    """
    return f"""
请搜索{province}{industry}产业链各环节的头部公司信息。

搜索要求：
1. 上游产业链：原材料、零部件、设备供应商等
2. 中游产业链：制造商、平台商、技术提供商等
3. 下游产业链：应用商、服务商、终端客户等

对于每家公司，请收集：
- 公司名称和股票代码（如有）
- 所属产业链环节
- 市场地位和市场份额
- 营收规模和毛利率
- 核心产品和竞争优势

请优先关注：
1. 行业龙头企业
2. 上市公司
3. {province}本地企业
4. 高成长性企业

搜索关键词建议：
- "{industry} 龙头企业"
- "{industry} 上市公司"
- "{province} {industry} 企业"
- "{industry} 产业链 企业"
- "{industry} 供应商"
- "{industry} 应用企业"
"""


if __name__ == "__main__":
    # 测试代码
    test_text = """
    人工智能产业链分析：
    
    上游方面，英伟达（NVDA）作为GPU芯片龙头，市场份额超过80%，2023年营收约600亿美元，毛利率高达70%。
    国内芯片企业寒武纪（688256）专注于AI芯片，营收约7亿元，毛利率约65%。
    
    中游平台层，百度（BIDU）的文心一言是国内领先的大模型平台，阿里云（BABA）提供云计算基础设施。
    科大讯飞（002230）在语音识别领域市场份额超过60%，2023年营收约200亿元，毛利率约40%。
    
    下游应用方面，海康威视（002415）是安防AI应用龙头，营收约800亿元，毛利率约45%。
    商汤科技（0020.HK）专注于计算机视觉应用。
    """
    
    engine = CompanyDiscoveryEngine()
    companies = engine.discover_from_research_data(test_text, "人工智能", "浙江省")
    
    print(f"发现公司数量: {len(companies)}")
    for c in companies:
        print(f"- {c.name}: {c.segment}-{c.sub_segment}, {c.market_position}, 置信度: {c.confidence:.2f}")
    
    print("\n" + "="*50 + "\n")
    print(engine.generate_discovery_report())
