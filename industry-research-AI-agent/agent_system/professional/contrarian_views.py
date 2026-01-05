# agent_system/professional/contrarian_views.py
"""
反共识观点模块
解决差距五：缺少观点冲突与反共识

核心理念：
- 不只是"安全正确"的判断
- 而是"有立场的投资人"视角
- 包含：市场主流观点、反共识判断、论证逻辑
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ViewType(Enum):
    """观点类型"""
    CONSENSUS = "市场共识"
    CONTRARIAN = "反共识"
    DIFFERENTIATED = "差异化"


class ConvictionLevel(Enum):
    """确信度"""
    HIGH = "高确信"
    MEDIUM = "中等确信"
    LOW = "低确信"


class TimeHorizon(Enum):
    """时间维度"""
    SHORT = "短期（1年内）"
    MEDIUM = "中期（1-3年）"
    LONG = "长期（3年以上）"


@dataclass
class MarketConsensus:
    """市场共识"""
    topic: str                  # 议题
    consensus_view: str         # 共识观点
    supporting_evidence: List[str] = field(default_factory=list)  # 支撑证据
    believers: List[str] = field(default_factory=list)  # 持有者（机构/分析师）
    prevalence: float = 0.8     # 普遍程度 0-1


@dataclass
class ContrarianArgument:
    """反共识论证"""
    argument: str               # 论点
    evidence: List[str] = field(default_factory=list)  # 证据
    data_support: List[str] = field(default_factory=list)  # 数据支撑
    logical_chain: str = ""     # 逻辑链条
    potential_catalysts: List[str] = field(default_factory=list)  # 潜在催化剂


@dataclass
class ContrarianView:
    """反共识观点"""
    topic: str                  # 议题
    
    # 市场共识
    market_consensus: MarketConsensus = None
    
    # 我们的观点
    our_view: str = ""
    view_type: ViewType = ViewType.CONTRARIAN
    conviction: ConvictionLevel = ConvictionLevel.MEDIUM
    time_horizon: TimeHorizon = TimeHorizon.MEDIUM
    
    # 论证
    arguments: List[ContrarianArgument] = field(default_factory=list)
    
    # 风险与验证
    risks_if_wrong: List[str] = field(default_factory=list)  # 如果错了的风险
    validation_milestones: List[str] = field(default_factory=list)  # 验证里程碑
    
    # 投资含义
    investment_implications: List[str] = field(default_factory=list)
    
    def generate_view_report(self) -> str:
        """生成观点报告"""
        report = f"## 反共识观点：{self.topic}\n\n"
        
        # 市场共识
        if self.market_consensus:
            report += "### 市场共识\n\n"
            report += f"> {self.market_consensus.consensus_view}\n\n"
            report += f"**普遍程度**：{self.market_consensus.prevalence:.0%}的市场参与者持此观点\n\n"
            
            if self.market_consensus.supporting_evidence:
                report += "**支撑证据**：\n"
                for ev in self.market_consensus.supporting_evidence:
                    report += f"- {ev}\n"
                report += "\n"
        
        # 我们的观点
        report += "### 我们的观点\n\n"
        report += f"> **{self.our_view}**\n\n"
        report += f"- **观点类型**：{self.view_type.value}\n"
        report += f"- **确信度**：{self.conviction.value}\n"
        report += f"- **时间维度**：{self.time_horizon.value}\n\n"
        
        # 论证
        if self.arguments:
            report += "### 核心论证\n\n"
            for i, arg in enumerate(self.arguments, 1):
                report += f"#### 论点{i}：{arg.argument}\n\n"
                
                if arg.evidence:
                    report += "**证据**：\n"
                    for ev in arg.evidence:
                        report += f"- {ev}\n"
                    report += "\n"
                
                if arg.data_support:
                    report += "**数据支撑**：\n"
                    for data in arg.data_support:
                        report += f"- {data}\n"
                    report += "\n"
                
                if arg.logical_chain:
                    report += f"**逻辑链条**：{arg.logical_chain}\n\n"
        
        # 风险
        if self.risks_if_wrong:
            report += "### 如果我们错了\n\n"
            for risk in self.risks_if_wrong:
                report += f"- {risk}\n"
            report += "\n"
        
        # 验证里程碑
        if self.validation_milestones:
            report += "### 验证里程碑\n\n"
            for milestone in self.validation_milestones:
                report += f"- {milestone}\n"
            report += "\n"
        
        # 投资含义
        if self.investment_implications:
            report += "### 投资含义\n\n"
            for impl in self.investment_implications:
                report += f"- {impl}\n"
        
        return report


class ContrarianViewGenerator:
    """反共识观点生成器"""
    
    # AI行业常见共识与反共识
    AI_INDUSTRY_DEBATES = {
        "中游平台价值": {
            "consensus": {
                "view": "AI中游平台（模型服务、AI中台）具有高价值，值得高估值",
                "evidence": [
                    "平台化模式可复制性强",
                    "技术壁垒高",
                    "客户粘性强"
                ],
                "prevalence": 0.7
            },
            "contrarian": {
                "view": "大模型崛起将压缩中游平台价值，中游可能成为'夹心层'",
                "arguments": [
                    {
                        "argument": "大模型具备端到端能力，绕过中游",
                        "evidence": [
                            "GPT-4等大模型可直接完成原本需要中游平台的任务",
                            "云厂商自建大模型，减少对第三方平台依赖"
                        ],
                        "data_support": [
                            "2024年大模型API调用量同比增长300%",
                            "中游AI平台客单价下降15-20%"
                        ]
                    },
                    {
                        "argument": "上下游挤压中游利润空间",
                        "evidence": [
                            "上游算力成本居高不下",
                            "下游客户议价能力增强"
                        ]
                    }
                ],
                "risks_if_wrong": [
                    "大模型落地不及预期，中游平台仍有存在价值",
                    "垂直领域know-how仍需中游平台承载"
                ],
                "investment_implications": [
                    "谨慎投资纯中游平台公司",
                    "关注有上游（算力/模型）或下游（场景）延伸能力的公司"
                ]
            }
        },
        "浙江AI地位": {
            "consensus": {
                "view": "浙江AI产业实力强劲，位居全国第一梯队",
                "evidence": [
                    "阿里巴巴总部所在地",
                    "数字经济先发优势",
                    "政策支持力度大"
                ],
                "prevalence": 0.8
            },
            "contrarian": {
                "view": "浙江在AI上游（芯片、大模型）可能被北京/广东拉开差距",
                "arguments": [
                    {
                        "argument": "AI上游人才和资源向北京集中",
                        "evidence": [
                            "北京拥有清华、北大等顶尖AI人才",
                            "字节、百度、智谱等大模型公司总部在北京",
                            "北京AI论文数量是浙江的3倍"
                        ],
                        "data_support": [
                            "2024年AI融资额：北京占全国45%，浙江仅15%",
                            "大模型创业公司：北京50+家，浙江不足10家"
                        ]
                    },
                    {
                        "argument": "广东在AI芯片领域快速追赶",
                        "evidence": [
                            "华为海思、比亚迪半导体等芯片企业",
                            "深圳AI芯片产业链更完整"
                        ]
                    }
                ],
                "risks_if_wrong": [
                    "阿里云大模型突破，带动浙江AI上游发展",
                    "浙江政府加大AI上游投入，吸引人才回流"
                ],
                "investment_implications": [
                    "浙江AI投资重点放在应用层（智能制造、安防）",
                    "上游投资需谨慎，关注与阿里生态协同的项目"
                ]
            }
        },
        "AI安防天花板": {
            "consensus": {
                "view": "AI安防市场已趋于成熟，增长空间有限",
                "evidence": [
                    "国内安防市场增速降至个位数",
                    "海康、大华双寡头格局稳固",
                    "政府安防预算增长放缓"
                ],
                "prevalence": 0.6
            },
            "contrarian": {
                "view": "AI安防正在从'安防'向'视觉智能'升级，打开新增长空间",
                "arguments": [
                    {
                        "argument": "视觉AI应用场景远超传统安防",
                        "evidence": [
                            "工业质检、智慧零售、智慧城市等新场景",
                            "海康创新业务（萤石、机器人）增速超30%"
                        ],
                        "data_support": [
                            "海康创新业务收入占比从5%提升至12%",
                            "视觉AI市场规模是传统安防的3倍"
                        ]
                    },
                    {
                        "argument": "海外市场仍有较大空间",
                        "evidence": [
                            "海康海外收入占比仅25%，低于全球化企业平均50%",
                            "东南亚、中东等新兴市场快速增长"
                        ]
                    }
                ],
                "risks_if_wrong": [
                    "美国制裁加剧，海外拓展受阻",
                    "创新业务竞争加剧，盈利能力下降"
                ],
                "investment_implications": [
                    "关注海康、大华的创新业务进展",
                    "视觉AI应用层可能出现新龙头"
                ]
            }
        }
    }
    
    def __init__(self):
        pass
    
    def get_industry_debates(self, industry: str) -> List[Dict]:
        """获取行业争议话题"""
        debates = []
        for topic, data in self.AI_INDUSTRY_DEBATES.items():
            debates.append({
                "topic": topic,
                "consensus": data["consensus"],
                "contrarian": data["contrarian"]
            })
        return debates
    
    def create_contrarian_view(
        self,
        topic: str,
        consensus_view: str,
        our_view: str,
        arguments: List[Dict],
        conviction: str = "MEDIUM",
        time_horizon: str = "MEDIUM"
    ) -> ContrarianView:
        """创建反共识观点"""
        
        # 创建市场共识
        market_consensus = MarketConsensus(
            topic=topic,
            consensus_view=consensus_view
        )
        
        # 创建论证
        contrarian_arguments = []
        for arg_data in arguments:
            arg = ContrarianArgument(
                argument=arg_data.get("argument", ""),
                evidence=arg_data.get("evidence", []),
                data_support=arg_data.get("data_support", []),
                logical_chain=arg_data.get("logical_chain", "")
            )
            contrarian_arguments.append(arg)
        
        # 创建反共识观点
        view = ContrarianView(
            topic=topic,
            market_consensus=market_consensus,
            our_view=our_view,
            view_type=ViewType.CONTRARIAN,
            conviction=ConvictionLevel[conviction],
            time_horizon=TimeHorizon[time_horizon],
            arguments=contrarian_arguments
        )
        
        return view
    
    def generate_contrarian_section(self, industry: str, province: str) -> str:
        """生成反共识观点章节"""
        
        report = "# 反共识观点与差异化判断\n\n"
        report += "> 以下观点可能与市场主流判断不同，我们提供论证逻辑供投资者参考。\n\n"
        
        # 获取相关争议
        debates = self.get_industry_debates(industry)
        
        for debate in debates:
            topic = debate["topic"]
            consensus = debate["consensus"]
            contrarian = debate["contrarian"]
            
            # 创建反共识观点
            view = ContrarianView(
                topic=topic,
                market_consensus=MarketConsensus(
                    topic=topic,
                    consensus_view=consensus["view"],
                    supporting_evidence=consensus.get("evidence", []),
                    prevalence=consensus.get("prevalence", 0.7)
                ),
                our_view=contrarian["view"],
                view_type=ViewType.CONTRARIAN,
                conviction=ConvictionLevel.MEDIUM,
                time_horizon=TimeHorizon.MEDIUM,
                risks_if_wrong=contrarian.get("risks_if_wrong", []),
                investment_implications=contrarian.get("investment_implications", [])
            )
            
            # 添加论证
            for arg_data in contrarian.get("arguments", []):
                arg = ContrarianArgument(
                    argument=arg_data.get("argument", ""),
                    evidence=arg_data.get("evidence", []),
                    data_support=arg_data.get("data_support", [])
                )
                view.arguments.append(arg)
            
            report += view.generate_view_report()
            report += "\n---\n\n"
        
        return report


# 创建全局实例
contrarian_view_generator = ContrarianViewGenerator()


# Prompt模板：反共识观点
CONTRARIAN_VIEW_PROMPT = """
【反共识观点分析要求】

你正在进行专业级投资研究，需要展现"有立场的投资人"视角：

## 一、识别市场共识

首先，明确市场主流观点：

### 共识观点模板
**议题**：XXX
**市场共识**：XXX
**普遍程度**：XX%的市场参与者持此观点
**支撑证据**：
- 证据1
- 证据2

## 二、提出反共识判断

对于每个重要议题，必须回答：
1. 市场普遍认为什么？
2. 我们认为什么是错误的？
3. 我们的判断是什么？
4. 我们的论证逻辑是什么？

### 反共识观点模板

**议题**：XXX

**市场共识**：
> "XXX"（XX%的市场参与者持此观点）

**我们的观点**：
> **XXX**（与市场共识不同）

**核心论证**：

**论点1**：XXX
- 证据：
- 数据支撑：
- 逻辑链条：

**论点2**：XXX
- 证据：
- 数据支撑：

**如果我们错了**：
- 风险1
- 风险2

**验证里程碑**：
- 里程碑1（时间点）
- 里程碑2（时间点）

**投资含义**：
- 含义1
- 含义2

## 三、必须覆盖的争议话题

针对本次研究，必须对以下话题给出反共识判断：

1. **行业增长**：市场对增速的预期是否过于乐观/悲观？
2. **竞争格局**：龙头地位是否真的稳固？
3. **估值水平**：当前估值是否合理？
4. **技术路线**：主流技术路线是否正确？
5. **政策影响**：政策利好是否被过度解读？

## 四、观点质量要求

✅ 好的反共识观点：
- 有明确的市场共识作为对照
- 有数据和证据支撑
- 有清晰的逻辑链条
- 承认可能错误的风险
- 有明确的验证方式

❌ 差的反共识观点：
- 为了反对而反对
- 没有数据支撑
- 逻辑不清晰
- 不承认风险
- 无法验证

---

**顶级研报的反共识特征**：
> "市场普遍认为 XX，但我们认为 XX 是错误的，因为..."
"""


def get_contrarian_prompt(industry: str, province: str) -> str:
    """获取反共识观点Prompt"""
    return f"""
{CONTRARIAN_VIEW_PROMPT}

【本次分析任务】
- 行业：{industry}
- 区域：{province}

请针对以下议题提出反共识判断：

1. {province}{industry}市场增速是否被高估？
2. 龙头企业的竞争优势是否可持续？
3. 当前估值水平是否合理？
4. 主流技术路线是否正确？
5. 政策红利是否被过度解读？

每个反共识观点必须：
- 明确市场共识
- 给出我们的判断
- 提供论证逻辑
- 承认错误风险
- 说明投资含义
"""
