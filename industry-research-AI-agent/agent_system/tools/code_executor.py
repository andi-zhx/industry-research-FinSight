# agent_system/tools/code_executor.py
"""
Python代码执行器
让Agent能够执行Python代码进行计算型分析

核心功能：
1. 安全沙箱执行 - 限制危险操作
2. 数据分析支持 - 预装pandas、numpy等
3. 结果格式化 - 将计算结果转为可读格式
4. 错误处理 - 优雅处理执行错误
"""

import io
import sys
import traceback
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from contextlib import redirect_stdout, redirect_stderr
import ast


@dataclass
class ExecutionResult:
    """代码执行结果"""
    success: bool
    output: str
    error: str = ""
    variables: Dict[str, Any] = None
    execution_time: float = 0.0
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}


class SafeCodeExecutor:
    """
    安全的Python代码执行器
    限制危险操作，提供数据分析环境
    """
    
    # 禁止的模块
    FORBIDDEN_MODULES = {
        'os', 'subprocess', 'sys', 'shutil', 'socket', 
        'requests', 'urllib', 'http', 'ftplib', 'smtplib',
        'pickle', 'marshal', 'shelve', 'dbm',
        '__builtins__', 'builtins', 'importlib', 'imp'
    }
    
    # 禁止的内置函数
    FORBIDDEN_BUILTINS = {
        'exec', 'eval', 'compile', 'open', 'input',
        '__import__', 'globals', 'locals', 'vars',
        'getattr', 'setattr', 'delattr', 'hasattr'
    }
    
    # 允许的安全模块
    SAFE_MODULES = {
        'math', 'statistics', 'decimal', 'fractions',
        'datetime', 'calendar', 'collections', 'itertools',
        'functools', 'operator', 'string', 're',
        'json', 'csv', 'typing'
    }
    
    def __init__(self, timeout: int = 30, max_output_length: int = 10000):
        """
        初始化执行器
        
        Args:
            timeout: 执行超时时间（秒）
            max_output_length: 最大输出长度
        """
        self.timeout = timeout
        self.max_output_length = max_output_length
        self._setup_safe_globals()
    
    def _setup_safe_globals(self):
        """设置安全的全局环境"""
        import math
        import statistics
        import datetime
        import json
        import re
        from collections import defaultdict, Counter, OrderedDict
        
        # 安全的内置函数
        safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'bin': bin,
            'bool': bool, 'chr': chr, 'dict': dict, 'dir': dir,
            'divmod': divmod, 'enumerate': enumerate, 'filter': filter,
            'float': float, 'format': format, 'frozenset': frozenset,
            'hex': hex, 'int': int, 'isinstance': isinstance,
            'issubclass': issubclass, 'iter': iter, 'len': len,
            'list': list, 'map': map, 'max': max, 'min': min,
            'next': next, 'oct': oct, 'ord': ord, 'pow': pow,
            'print': print, 'range': range, 'repr': repr,
            'reversed': reversed, 'round': round, 'set': set,
            'slice': slice, 'sorted': sorted, 'str': str,
            'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
            'True': True, 'False': False, 'None': None,
        }
        
        self.safe_globals = {
            '__builtins__': safe_builtins,
            'math': math,
            'statistics': statistics,
            'datetime': datetime,
            'json': json,
            're': re,
            'defaultdict': defaultdict,
            'Counter': Counter,
            'OrderedDict': OrderedDict,
        }
        
        # 尝试导入数据分析库
        try:
            import pandas as pd
            import numpy as np
            self.safe_globals['pd'] = pd
            self.safe_globals['np'] = np
            self.safe_globals['DataFrame'] = pd.DataFrame
            self.safe_globals['Series'] = pd.Series
        except ImportError:
            pass
        
        try:
            import numpy_financial as npf
            self.safe_globals['npf'] = npf
        except ImportError:
            pass
    
    def _validate_code(self, code: str) -> tuple:
        """
        验证代码安全性
        
        Args:
            code: 待验证的代码
        
        Returns:
            tuple: (is_safe, error_message)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"语法错误: {e}"
        
        # 检查导入语句
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] in self.FORBIDDEN_MODULES:
                        return False, f"禁止导入模块: {alias.name}"
            
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] in self.FORBIDDEN_MODULES:
                    return False, f"禁止导入模块: {node.module}"
            
            # 检查危险函数调用
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.FORBIDDEN_BUILTINS:
                        return False, f"禁止调用函数: {node.func.id}"
                elif isinstance(node.func, ast.Attribute):
                    # 检查 os.system 等
                    if isinstance(node.func.value, ast.Name):
                        if node.func.value.id in self.FORBIDDEN_MODULES:
                            return False, f"禁止访问模块: {node.func.value.id}"
        
        return True, ""
    
    def execute(self, code: str, local_vars: Dict[str, Any] = None) -> ExecutionResult:
        """
        执行Python代码
        
        Args:
            code: 要执行的代码
            local_vars: 局部变量
        
        Returns:
            ExecutionResult: 执行结果
        """
        import time
        
        # 验证代码安全性
        is_safe, error = self._validate_code(code)
        if not is_safe:
            return ExecutionResult(
                success=False,
                output="",
                error=f"代码安全检查失败: {error}"
            )
        
        # 准备执行环境
        exec_globals = self.safe_globals.copy()
        exec_locals = local_vars.copy() if local_vars else {}
        
        # 捕获输出
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        start_time = time.time()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, exec_globals, exec_locals)
            
            execution_time = time.time() - start_time
            
            # 获取输出
            output = stdout_capture.getvalue()
            if len(output) > self.max_output_length:
                output = output[:self.max_output_length] + "\n... (输出被截断)"
            
            # 提取结果变量
            result_vars = {}
            for key, value in exec_locals.items():
                if not key.startswith('_'):
                    try:
                        # 尝试序列化
                        if hasattr(value, 'to_dict'):
                            result_vars[key] = value.to_dict()
                        elif hasattr(value, 'tolist'):
                            result_vars[key] = value.tolist()
                        else:
                            result_vars[key] = str(value)[:1000]
                    except:
                        result_vars[key] = f"<{type(value).__name__}>"
            
            return ExecutionResult(
                success=True,
                output=output,
                variables=result_vars,
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            
            return ExecutionResult(
                success=False,
                output=stdout_capture.getvalue(),
                error=error_msg,
                execution_time=execution_time
            )


class FinancialCalculator:
    """
    金融计算器
    提供常用的金融计算功能
    """
    
    def __init__(self, executor: SafeCodeExecutor = None):
        self.executor = executor or SafeCodeExecutor()
    
    def calculate_cagr(self, start_value: float, end_value: float, 
                       years: int) -> Dict[str, Any]:
        """计算复合年增长率"""
        code = f"""
import math
start_value = {start_value}
end_value = {end_value}
years = {years}

if start_value > 0 and years > 0:
    cagr = (pow(end_value / start_value, 1 / years) - 1) * 100
    result = f"CAGR = {{cagr:.2f}}%"
    print(result)
else:
    result = "无法计算：起始值或年数无效"
    print(result)
"""
        result = self.executor.execute(code)
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error
        }
    
    def calculate_irr(self, cash_flows: List[float]) -> Dict[str, Any]:
        """计算内部收益率"""
        code = f"""
import numpy_financial as npf
cash_flows = {cash_flows}
irr = npf.irr(cash_flows)
if irr is not None:
    result = f"IRR = {{irr * 100:.2f}}%"
else:
    result = "无法计算IRR（现金流可能无解）"
print(result)
"""
        result = self.executor.execute(code)
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error
        }
    
    def calculate_npv(self, rate: float, cash_flows: List[float]) -> Dict[str, Any]:
        """计算净现值"""
        code = f"""
import numpy_financial as npf
rate = {rate}
cash_flows = {cash_flows}
npv = npf.npv(rate, cash_flows)
result = f"NPV = {{npv:,.2f}}"
print(result)
"""
        result = self.executor.execute(code)
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error
        }
    
    def calculate_market_share(self, company_revenue: float, 
                                market_size: float) -> Dict[str, Any]:
        """计算市场份额"""
        code = f"""
company_revenue = {company_revenue}
market_size = {market_size}
if market_size > 0:
    market_share = (company_revenue / market_size) * 100
    result = f"市场份额 = {{market_share:.2f}}%"
else:
    result = "无法计算：市场规模无效"
print(result)
"""
        result = self.executor.execute(code)
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error
        }
    
    def analyze_growth_trend(self, values: List[float], 
                              years: List[int]) -> Dict[str, Any]:
        """分析增长趋势"""
        code = f"""
import statistics
values = {values}
years = {years}

# 计算年增长率
growth_rates = []
for i in range(1, len(values)):
    if values[i-1] > 0:
        rate = (values[i] - values[i-1]) / values[i-1] * 100
        growth_rates.append(rate)

if growth_rates:
    avg_growth = statistics.mean(growth_rates)
    max_growth = max(growth_rates)
    min_growth = min(growth_rates)
    
    print(f"平均增长率: {{avg_growth:.2f}}%")
    print(f"最高增长率: {{max_growth:.2f}}%")
    print(f"最低增长率: {{min_growth:.2f}}%")
    
    # 判断趋势
    if len(growth_rates) >= 2:
        recent_avg = statistics.mean(growth_rates[-2:])
        early_avg = statistics.mean(growth_rates[:2])
        if recent_avg > early_avg:
            print("趋势: 增长加速")
        elif recent_avg < early_avg:
            print("趋势: 增长放缓")
        else:
            print("趋势: 稳定增长")
else:
    print("数据不足，无法分析趋势")
"""
        result = self.executor.execute(code)
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error
        }


class DataTableGenerator:
    """
    数据表格生成器
    将数据转换为Markdown表格
    """
    
    def __init__(self, executor: SafeCodeExecutor = None):
        self.executor = executor or SafeCodeExecutor()
    
    def generate_comparison_table(self, data: Dict[str, Dict]) -> str:
        """
        生成对比表格
        
        Args:
            data: {公司名: {指标: 值}}
        
        Returns:
            str: Markdown表格
        """
        code = f"""
import pandas as pd
data = {data}
df = pd.DataFrame(data).T
print(df.to_markdown())
"""
        result = self.executor.execute(code)
        if result.success:
            return result.output
        return f"表格生成失败: {result.error}"
    
    def generate_time_series_table(self, data: Dict[str, List], 
                                    years: List[int]) -> str:
        """
        生成时间序列表格
        
        Args:
            data: {指标: [值列表]}
            years: 年份列表
        
        Returns:
            str: Markdown表格
        """
        code = f"""
import pandas as pd
data = {data}
years = {years}
df = pd.DataFrame(data, index=years)
df.index.name = '年份'
print(df.to_markdown())
"""
        result = self.executor.execute(code)
        if result.success:
            return result.output
        return f"表格生成失败: {result.error}"


# 全局实例
code_executor = SafeCodeExecutor()
financial_calculator = FinancialCalculator(code_executor)
data_table_generator = DataTableGenerator(code_executor)
