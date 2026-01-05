# utils/chart_generator.py
"""
数据图表生成模块
使用matplotlib生成专业金融风格的图表
支持折线图、柱形图、饼图、面积图等
"""

import os
import base64
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Union
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# FinSight专业配色方案
FINSIGHT_COLORS = {
    'primary': '#1E40AF',      # 深蓝
    'secondary': '#3B82F6',    # 蓝色
    'accent': '#00D4FF',       # 电光蓝
    'success': '#10B981',      # 绿色
    'warning': '#F59E0B',      # 橙色
    'danger': '#EF4444',       # 红色
    'neutral': '#64748B',      # 灰色
    'background': '#0F172A',   # 深色背景
    'text': '#E2E8F0',         # 浅色文字
}

# 图表配色序列
CHART_PALETTE = [
    '#3B82F6',  # 蓝色
    '#10B981',  # 绿色
    '#F59E0B',  # 橙色
    '#EF4444',  # 红色
    '#8B5CF6',  # 紫色
    '#EC4899',  # 粉色
    '#06B6D4',  # 青色
    '#84CC16',  # 黄绿
]


class ChartGenerator:
    """
    专业金融图表生成器
    """
    
    def __init__(self, style: str = 'dark', output_dir: str = './charts'):
        """
        初始化图表生成器
        
        Args:
            style: 图表风格 ('dark' 或 'light')
            output_dir: 图表输出目录
        """
        self.style = style
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置全局样式
        self._setup_style()
    
    def _setup_style(self):
        """设置图表样式"""
        if self.style == 'dark':
            plt.style.use('dark_background')
            self.bg_color = '#0F172A'
            self.text_color = '#E2E8F0'
            self.grid_color = '#334155'
            self.spine_color = '#475569'
        else:
            plt.style.use('seaborn-v0_8-whitegrid')
            self.bg_color = '#FFFFFF'
            self.text_color = '#1E293B'
            self.grid_color = '#E2E8F0'
            self.spine_color = '#CBD5E1'
    
    def _create_figure(self, figsize: Tuple[int, int] = (10, 6)) -> Tuple[plt.Figure, plt.Axes]:
        """创建图表画布"""
        fig, ax = plt.subplots(figsize=figsize, facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)
        
        # 设置边框颜色
        for spine in ax.spines.values():
            spine.set_color(self.spine_color)
        
        # 设置刻度颜色
        ax.tick_params(colors=self.text_color)
        ax.xaxis.label.set_color(self.text_color)
        ax.yaxis.label.set_color(self.text_color)
        
        return fig, ax
    
    def _save_chart(self, fig: plt.Figure, filename: str) -> str:
        """保存图表"""
        filepath = os.path.join(self.output_dir, filename)
        fig.savefig(filepath, dpi=150, bbox_inches='tight', 
                   facecolor=self.bg_color, edgecolor='none')
        plt.close(fig)
        return filepath
    
    def _to_base64(self, fig: plt.Figure) -> str:
        """将图表转换为Base64编码"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor=self.bg_color, edgecolor='none')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return f"data:image/png;base64,{img_base64}"
    
    def line_chart(
        self,
        x_data: List,
        y_data: Union[List, Dict[str, List]],
        title: str = "",
        x_label: str = "",
        y_label: str = "",
        filename: str = None,
        show_markers: bool = True,
        fill_area: bool = False,
        target_line: float = None,
        annotations: List[Dict] = None
    ) -> str:
        """
        生成折线图
        
        Args:
            x_data: X轴数据
            y_data: Y轴数据（单系列为List，多系列为Dict）
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            filename: 输出文件名
            show_markers: 是否显示数据点
            fill_area: 是否填充面积
            target_line: 目标线值
            annotations: 标注列表
        
        Returns:
            图表文件路径或Base64编码
        """
        fig, ax = self._create_figure()
        
        # 处理多系列数据
        if isinstance(y_data, dict):
            for i, (label, values) in enumerate(y_data.items()):
                color = CHART_PALETTE[i % len(CHART_PALETTE)]
                marker = 'o' if show_markers else None
                ax.plot(x_data, values, label=label, color=color, 
                       marker=marker, markersize=6, linewidth=2)
                if fill_area:
                    ax.fill_between(x_data, values, alpha=0.2, color=color)
            ax.legend(facecolor=self.bg_color, edgecolor=self.spine_color,
                     labelcolor=self.text_color)
        else:
            color = CHART_PALETTE[0]
            marker = 'o' if show_markers else None
            ax.plot(x_data, y_data, color=color, marker=marker, 
                   markersize=6, linewidth=2)
            if fill_area:
                ax.fill_between(x_data, y_data, alpha=0.2, color=color)
        
        # 添加目标线
        if target_line is not None:
            ax.axhline(y=target_line, color=FINSIGHT_COLORS['warning'], 
                      linestyle='--', linewidth=1.5, label=f'Target: {target_line}')
        
        # 添加标注
        if annotations:
            for ann in annotations:
                ax.annotate(ann.get('text', ''), 
                           xy=(ann.get('x'), ann.get('y')),
                           xytext=(ann.get('x_offset', 10), ann.get('y_offset', 10)),
                           textcoords='offset points',
                           color=self.text_color,
                           fontsize=9,
                           arrowprops=dict(arrowstyle='->', color=self.text_color))
        
        # 设置标题和标签
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(x_label, color=self.text_color, fontsize=11)
        ax.set_ylabel(y_label, color=self.text_color, fontsize=11)
        
        # 设置网格
        ax.grid(True, linestyle='--', alpha=0.3, color=self.grid_color)
        
        # 旋转X轴标签
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        if filename:
            return self._save_chart(fig, filename)
        return self._to_base64(fig)
    
    def bar_chart(
        self,
        categories: List[str],
        values: Union[List, Dict[str, List]],
        title: str = "",
        x_label: str = "",
        y_label: str = "",
        filename: str = None,
        horizontal: bool = False,
        show_values: bool = True,
        stacked: bool = False
    ) -> str:
        """
        生成柱形图
        
        Args:
            categories: 类别列表
            values: 数值（单系列为List，多系列为Dict）
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            filename: 输出文件名
            horizontal: 是否水平显示
            show_values: 是否显示数值标签
            stacked: 是否堆叠
        
        Returns:
            图表文件路径或Base64编码
        """
        fig, ax = self._create_figure()
        
        x = np.arange(len(categories))
        
        if isinstance(values, dict):
            # 多系列柱形图
            n_series = len(values)
            width = 0.8 / n_series if not stacked else 0.6
            
            bottom = np.zeros(len(categories)) if stacked else None
            
            for i, (label, vals) in enumerate(values.items()):
                color = CHART_PALETTE[i % len(CHART_PALETTE)]
                offset = (i - n_series/2 + 0.5) * width if not stacked else 0
                
                if horizontal:
                    if stacked:
                        bars = ax.barh(x, vals, width, left=bottom, label=label, color=color)
                        bottom += np.array(vals)
                    else:
                        bars = ax.barh(x + offset, vals, width, label=label, color=color)
                else:
                    if stacked:
                        bars = ax.bar(x, vals, width, bottom=bottom, label=label, color=color)
                        bottom += np.array(vals)
                    else:
                        bars = ax.bar(x + offset, vals, width, label=label, color=color)
                
                # 显示数值
                if show_values:
                    for bar, val in zip(bars, vals):
                        if horizontal:
                            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                                   f'{val:.1f}', va='center', color=self.text_color, fontsize=8)
                        else:
                            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                                   f'{val:.1f}', ha='center', color=self.text_color, fontsize=8)
            
            ax.legend(facecolor=self.bg_color, edgecolor=self.spine_color,
                     labelcolor=self.text_color)
        else:
            # 单系列柱形图
            colors = [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(values))]
            
            if horizontal:
                bars = ax.barh(x, values, color=colors)
            else:
                bars = ax.bar(x, values, color=colors)
            
            # 显示数值
            if show_values:
                for bar, val in zip(bars, values):
                    if horizontal:
                        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                               f'{val:.1f}', va='center', color=self.text_color, fontsize=9)
                    else:
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                               f'{val:.1f}', ha='center', color=self.text_color, fontsize=9)
        
        # 设置标签
        if horizontal:
            ax.set_yticks(x)
            ax.set_yticklabels(categories)
            ax.set_xlabel(y_label, color=self.text_color, fontsize=11)
            ax.set_ylabel(x_label, color=self.text_color, fontsize=11)
        else:
            ax.set_xticks(x)
            ax.set_xticklabels(categories, rotation=45, ha='right')
            ax.set_xlabel(x_label, color=self.text_color, fontsize=11)
            ax.set_ylabel(y_label, color=self.text_color, fontsize=11)
        
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=15)
        ax.grid(True, linestyle='--', alpha=0.3, color=self.grid_color, axis='y' if not horizontal else 'x')
        
        plt.tight_layout()
        
        if filename:
            return self._save_chart(fig, filename)
        return self._to_base64(fig)
    
    def pie_chart(
        self,
        labels: List[str],
        values: List[float],
        title: str = "",
        filename: str = None,
        show_percentage: bool = True,
        explode_index: int = None,
        donut: bool = False
    ) -> str:
        """
        生成饼图
        
        Args:
            labels: 标签列表
            values: 数值列表
            title: 图表标题
            filename: 输出文件名
            show_percentage: 是否显示百分比
            explode_index: 突出显示的扇区索引
            donut: 是否为环形图
        
        Returns:
            图表文件路径或Base64编码
        """
        fig, ax = self._create_figure(figsize=(10, 8))
        
        colors = [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(values))]
        
        # 设置突出显示
        explode = [0] * len(values)
        if explode_index is not None and 0 <= explode_index < len(values):
            explode[explode_index] = 0.1
        
        # 绘制饼图
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors,
            explode=explode,
            autopct='%1.1f%%' if show_percentage else None,
            startangle=90,
            pctdistance=0.75 if donut else 0.6,
            labeldistance=1.1
        )
        
        # 设置文字颜色
        for text in texts:
            text.set_color(self.text_color)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        # 环形图
        if donut:
            centre_circle = plt.Circle((0, 0), 0.5, fc=self.bg_color)
            ax.add_patch(centre_circle)
        
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=15)
        
        # 添加图例
        ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5),
                 facecolor=self.bg_color, edgecolor=self.spine_color,
                 labelcolor=self.text_color)
        
        plt.tight_layout()
        
        if filename:
            return self._save_chart(fig, filename)
        return self._to_base64(fig)
    
    def area_chart(
        self,
        x_data: List,
        y_data: Dict[str, List],
        title: str = "",
        x_label: str = "",
        y_label: str = "",
        filename: str = None,
        stacked: bool = True
    ) -> str:
        """
        生成面积图
        
        Args:
            x_data: X轴数据
            y_data: Y轴数据（Dict格式）
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            filename: 输出文件名
            stacked: 是否堆叠
        
        Returns:
            图表文件路径或Base64编码
        """
        fig, ax = self._create_figure()
        
        colors = [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(y_data))]
        
        if stacked:
            ax.stackplot(x_data, *y_data.values(), labels=y_data.keys(), 
                        colors=colors, alpha=0.8)
        else:
            for i, (label, values) in enumerate(y_data.items()):
                ax.fill_between(x_data, values, alpha=0.5, color=colors[i], label=label)
                ax.plot(x_data, values, color=colors[i], linewidth=2)
        
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(x_label, color=self.text_color, fontsize=11)
        ax.set_ylabel(y_label, color=self.text_color, fontsize=11)
        ax.legend(facecolor=self.bg_color, edgecolor=self.spine_color,
                 labelcolor=self.text_color)
        ax.grid(True, linestyle='--', alpha=0.3, color=self.grid_color)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if filename:
            return self._save_chart(fig, filename)
        return self._to_base64(fig)
    
    def waterfall_chart(
        self,
        categories: List[str],
        values: List[float],
        title: str = "",
        filename: str = None
    ) -> str:
        """
        生成瀑布图（用于展示增减变化）
        
        Args:
            categories: 类别列表
            values: 变化值列表
            title: 图表标题
            filename: 输出文件名
        
        Returns:
            图表文件路径或Base64编码
        """
        fig, ax = self._create_figure()
        
        # 计算累计值
        cumulative = np.cumsum(values)
        cumulative = np.insert(cumulative, 0, 0)
        
        # 绘制瀑布图
        for i, (cat, val) in enumerate(zip(categories, values)):
            if val >= 0:
                color = FINSIGHT_COLORS['success']
                bottom = cumulative[i]
            else:
                color = FINSIGHT_COLORS['danger']
                bottom = cumulative[i+1]
            
            ax.bar(i, abs(val), bottom=bottom, color=color, width=0.6)
            
            # 添加连接线
            if i < len(values) - 1:
                ax.plot([i + 0.3, i + 0.7], [cumulative[i+1], cumulative[i+1]], 
                       color=self.spine_color, linestyle='--', linewidth=1)
        
        # 添加数值标签
        for i, (val, cum) in enumerate(zip(values, cumulative[1:])):
            y_pos = cum if val >= 0 else cum + abs(val)
            ax.text(i, y_pos + max(abs(v) for v in values) * 0.02, 
                   f'{val:+.1f}', ha='center', color=self.text_color, fontsize=9)
        
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=15)
        ax.axhline(y=0, color=self.spine_color, linewidth=0.5)
        ax.grid(True, linestyle='--', alpha=0.3, color=self.grid_color, axis='y')
        
        plt.tight_layout()
        
        if filename:
            return self._save_chart(fig, filename)
        return self._to_base64(fig)
    
    def radar_chart(
        self,
        categories: List[str],
        values: Union[List, Dict[str, List]],
        title: str = "",
        filename: str = None
    ) -> str:
        """
        生成雷达图
        
        Args:
            categories: 维度列表
            values: 数值（单系列为List，多系列为Dict）
            title: 图表标题
            filename: 输出文件名
        
        Returns:
            图表文件路径或Base64编码
        """
        fig = plt.figure(figsize=(10, 8), facecolor=self.bg_color)
        ax = fig.add_subplot(111, polar=True)
        ax.set_facecolor(self.bg_color)
        
        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # 闭合
        
        if isinstance(values, dict):
            for i, (label, vals) in enumerate(values.items()):
                vals = vals + vals[:1]  # 闭合
                color = CHART_PALETTE[i % len(CHART_PALETTE)]
                ax.plot(angles, vals, 'o-', linewidth=2, label=label, color=color)
                ax.fill(angles, vals, alpha=0.25, color=color)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1),
                     facecolor=self.bg_color, edgecolor=self.spine_color,
                     labelcolor=self.text_color)
        else:
            vals = values + values[:1]
            ax.plot(angles, vals, 'o-', linewidth=2, color=CHART_PALETTE[0])
            ax.fill(angles, vals, alpha=0.25, color=CHART_PALETTE[0])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, color=self.text_color, fontsize=10)
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=20)
        
        # 设置网格颜色
        ax.yaxis.grid(True, color=self.grid_color, linestyle='--', alpha=0.5)
        ax.xaxis.grid(True, color=self.grid_color, linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        if filename:
            return self._save_chart(fig, filename)
        return self._to_base64(fig)
    
    def heatmap(
        self,
        data: List[List[float]],
        x_labels: List[str],
        y_labels: List[str],
        title: str = "",
        filename: str = None,
        show_values: bool = True
    ) -> str:
        """
        生成热力图
        
        Args:
            data: 二维数据矩阵
            x_labels: X轴标签
            y_labels: Y轴标签
            title: 图表标题
            filename: 输出文件名
            show_values: 是否显示数值
        
        Returns:
            图表文件路径或Base64编码
        """
        fig, ax = self._create_figure(figsize=(12, 8))
        
        data_array = np.array(data)
        im = ax.imshow(data_array, cmap='Blues', aspect='auto')
        
        # 设置刻度
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_yticks(np.arange(len(y_labels)))
        ax.set_xticklabels(x_labels, rotation=45, ha='right')
        ax.set_yticklabels(y_labels)
        
        # 显示数值
        if show_values:
            for i in range(len(y_labels)):
                for j in range(len(x_labels)):
                    val = data_array[i, j]
                    text_color = 'white' if val > data_array.max() * 0.5 else self.text_color
                    ax.text(j, i, f'{val:.1f}', ha='center', va='center',
                           color=text_color, fontsize=9)
        
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=15)
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax)
        cbar.ax.yaxis.set_tick_params(color=self.text_color)
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=self.text_color)
        
        plt.tight_layout()
        
        if filename:
            return self._save_chart(fig, filename)
        return self._to_base64(fig)


# 便捷函数
def create_market_trend_chart(
    years: List[str],
    market_size: List[float],
    growth_rate: List[float] = None,
    title: str = "市场规模趋势",
    output_dir: str = "./charts"
) -> str:
    """
    创建市场规模趋势图
    """
    generator = ChartGenerator(output_dir=output_dir)
    
    if growth_rate:
        fig, ax1 = generator._create_figure()
        
        # 柱形图 - 市场规模
        bars = ax1.bar(years, market_size, color=CHART_PALETTE[0], alpha=0.8, label='市场规模')
        ax1.set_ylabel('市场规模 (亿元)', color=generator.text_color)
        ax1.tick_params(axis='y', labelcolor=generator.text_color)
        
        # 折线图 - 增长率
        ax2 = ax1.twinx()
        ax2.plot(years, growth_rate, color=CHART_PALETTE[1], marker='o', linewidth=2, label='增长率')
        ax2.set_ylabel('增长率 (%)', color=generator.text_color)
        ax2.tick_params(axis='y', labelcolor=generator.text_color)
        ax2.set_facecolor('none')
        
        ax1.set_title(title, color=generator.text_color, fontsize=14, fontweight='bold')
        
        # 合并图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left',
                  facecolor=generator.bg_color, edgecolor=generator.spine_color,
                  labelcolor=generator.text_color)
        
        plt.tight_layout()
        filename = f"market_trend_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        return generator._save_chart(fig, filename)
    else:
        return generator.line_chart(
            years, market_size, title=title,
            x_label='年份', y_label='市场规模 (亿元)',
            fill_area=True,
            filename=f"market_trend_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        )


def create_supply_chain_profit_chart(
    segments: List[str],
    profit_margins: List[float],
    title: str = "产业链利润分布",
    output_dir: str = "./charts"
) -> str:
    """
    创建产业链利润分布图
    """
    generator = ChartGenerator(output_dir=output_dir)
    return generator.bar_chart(
        segments, profit_margins,
        title=title,
        x_label='产业链环节',
        y_label='毛利率 (%)',
        horizontal=True,
        filename=f"supply_chain_profit_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    )


def create_competitive_landscape_chart(
    companies: List[str],
    market_shares: List[float],
    title: str = "竞争格局分析",
    output_dir: str = "./charts"
) -> str:
    """
    创建竞争格局饼图
    """
    generator = ChartGenerator(output_dir=output_dir)
    return generator.pie_chart(
        companies, market_shares,
        title=title,
        donut=True,
        filename=f"competitive_landscape_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    )


if __name__ == "__main__":
    # 测试代码
    generator = ChartGenerator(output_dir="./test_charts")
    
    # 测试折线图
    years = ['2020', '2021', '2022', '2023', '2024', '2025E']
    market_size = [1000, 1200, 1500, 1800, 2200, 2800]
    
    path = generator.line_chart(
        years, market_size,
        title="人工智能市场规模趋势",
        x_label="年份",
        y_label="市场规模 (亿元)",
        fill_area=True,
        filename="test_line.png"
    )
    print(f"折线图已保存: {path}")
    
    # 测试柱形图
    segments = ['上游-芯片', '上游-算力', '中游-平台', '中游-应用', '下游-服务']
    margins = [45, 35, 25, 30, 20]
    
    path = generator.bar_chart(
        segments, margins,
        title="产业链各环节毛利率",
        y_label="毛利率 (%)",
        horizontal=True,
        filename="test_bar.png"
    )
    print(f"柱形图已保存: {path}")
    
    # 测试饼图
    companies = ['阿里云', '华为云', '腾讯云', '百度云', '其他']
    shares = [35, 25, 18, 12, 10]
    
    path = generator.pie_chart(
        companies, shares,
        title="云计算市场份额",
        donut=True,
        filename="test_pie.png"
    )
    print(f"饼图已保存: {path}")
