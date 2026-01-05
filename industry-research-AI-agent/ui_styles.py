# investment_agent_crewai/ui_styles.py
"""
FinSight AI Agent 前端样式模块 - 专业金融科技风格
设计理念：
1. 深色科技感主题 - 体现专业金融科技气质
2. 渐变与光效 - 增加视觉层次和现代感
3. 数据可视化友好 - 适合展示图表和数据
4. 响应式设计 - 适配不同屏幕尺寸
"""
import streamlit as st


def apply_landing_page_css():
    """
    官网首页专用 CSS：专业金融科技风格
    特点：深色主题、渐变效果、科技感动画、数据可视化友好
    """
    st.markdown("""
    <style>
        /* ================= 1. 全局重置与字体 ================= */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
        
        :root {
            /* 主色调 - 金融科技蓝 */
            --primary-color: #2563EB;
            --primary-light: #3B82F6;
            --primary-dark: #1D4ED8;
            
            /* 辅助色 - 科技感渐变 */
            --accent-cyan: #06B6D4;
            --accent-purple: #8B5CF6;
            --accent-green: #10B981;
            --accent-orange: #F59E0B;
            --accent-red: #EF4444;
            
            /* 深色背景系 */
            --bg-dark: #0A0F1C;
            --bg-card: #111827;
            --bg-card-hover: #1F2937;
            --bg-gradient: linear-gradient(135deg, #0A0F1C 0%, #111827 50%, #0F172A 100%);
            
            /* 文字色 */
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            
            /* 边框与分割线 */
            --border-color: rgba(59, 130, 246, 0.2);
            --border-glow: rgba(59, 130, 246, 0.5);
            
            /* 阴影 */
            --shadow-glow: 0 0 20px rgba(59, 130, 246, 0.3);
            --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.4);
        }
        
        .stApp {
            background: var(--bg-gradient);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: var(--text-primary);
        }
        
        /* 隐藏 Streamlit 原生干扰元素 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {visibility: hidden;}
        div[data-testid="stSidebar"] {display: none;}
        
        /* 调整页面边距 */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 5rem !important;
            max-width: 1400px !important;
        }

        /* ================= 2. 导航栏 (Navbar) ================= */
        .nav-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem 0;
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--border-color);
        }
        .nav-logo {
            font-size: 1.75rem;
            font-weight: 800;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
        }
        .nav-badge {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-cyan));
            color: white;
            font-size: 0.7rem;
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
        }

        /* ================= 3. Hero 区域 (大标题) ================= */
        .hero-section {
            text-align: center;
            padding: 4rem 0 3rem 0;
            position: relative;
        }
        .hero-section::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
            pointer-events: none;
        }
        .hero-title {
            font-size: 4.5rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
            position: relative;
            z-index: 1;
        }
        .hero-highlight {
            background: linear-gradient(135deg, var(--primary-light) 0%, var(--accent-cyan) 50%, var(--accent-purple) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient-shift 3s ease infinite;
        }
        @keyframes gradient-shift {
            0%, 100% { filter: hue-rotate(0deg); }
            50% { filter: hue-rotate(30deg); }
        }
        .hero-subtitle {
            font-size: 1.25rem;
            color: var(--text-secondary);
            max-width: 800px;
            margin: 0 auto;
            line-height: 1.8;
            position: relative;
            z-index: 1;
        }

        /* ================= 4. 核心指标卡片 (Metrics) ================= */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
            margin: 3rem 0;
        }
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 2rem 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-cyan));
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-8px);
            box-shadow: var(--shadow-glow);
            border-color: var(--border-glow);
        }
        .metric-card:hover::before {
            opacity: 1;
        }
        .metric-value {
            display: block;
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, var(--text-primary), var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            font-family: 'JetBrains Mono', monospace;
        }
        .metric-label {
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        /* ================= 5. 内容区块通用样式 ================= */
        .section-title {
            font-size: 2.25rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 4rem 0 2rem 0;
            text-align: center;
            position: relative;
        }
        .section-title::after {
            content: '';
            display: block;
            width: 80px;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-cyan));
            margin: 1rem auto 0;
            border-radius: 2px;
        }
        
        /* 6维度卡片 grid */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
        }
        .feature-card {
            background: var(--bg-card);
            padding: 2rem;
            border-radius: 16px;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .feature-card::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .feature-card:hover {
            background: var(--bg-card-hover);
            border-color: var(--border-glow);
            transform: translateY(-4px);
            box-shadow: var(--shadow-card);
        }
        .feature-card:hover::after {
            opacity: 1;
        }
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            display: inline-block;
            filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.5));
        }
        .feature-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.75rem;
        }
        .feature-desc {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
        }

        /* ================= 6. 产业链可视化 (三色块) ================= */
        .chain-wrapper {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 2.5rem;
            box-shadow: var(--shadow-card);
        }
        .chain-visual {
            display: flex;
            gap: 1.5rem;
            margin-top: 1.5rem;
        }
        .chain-step {
            flex: 1;
            padding: 2rem;
            border-radius: 16px;
            color: white;
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease;
        }
        .chain-step:hover {
            transform: scale(1.02);
        }
        .chain-step::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        }
        .chain-step h3 { 
            color: white !important; 
            margin-top: 0; 
            font-size: 1.25rem;
            position: relative;
            z-index: 1;
        }
        .chain-step p { 
            opacity: 0.9; 
            font-size: 0.9rem; 
            margin-bottom: 0;
            position: relative;
            z-index: 1;
            line-height: 1.6;
        }
        
        .bg-green { 
            background: linear-gradient(135deg, #059669 0%, #10B981 100%);
            box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
        }
        .bg-blue { 
            background: linear-gradient(135deg, #1D4ED8 0%, #3B82F6 100%);
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
        }
        .bg-orange { 
            background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%);
            box-shadow: 0 8px 32px rgba(245, 158, 11, 0.3);
        }

        /* ================= 7. 架构图 (Workflow) ================= */
        .workflow-container {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 2rem;
            padding: 2rem;
            background: var(--bg-card);
            border-radius: 16px;
            border: 1px solid var(--border-color);
        }
        .workflow-node {
            background: linear-gradient(135deg, var(--bg-card-hover), var(--bg-card));
            color: var(--text-primary);
            padding: 1rem 1.5rem;
            border-radius: 12px;
            font-weight: 600;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
            position: relative;
        }
        .workflow-node:hover {
            border-color: var(--primary-color);
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
            transform: translateY(-2px);
        }
        .workflow-arrow { 
            color: var(--accent-cyan); 
            font-size: 1.5rem;
            text-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
        }

        /* ================= 8. 自定义按钮样式 ================= */
        div[data-testid="column"]:nth-of-type(2) button {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-cyan)) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
        }
        div[data-testid="column"]:nth-of-type(2) button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5) !important;
        }

        /* ================= 9. 页脚 ================= */
        .footer {
            text-align: center;
            color: var(--text-muted);
            padding: 3rem 0;
            margin-top: 4rem;
            border-top: 1px solid var(--border-color);
        }
        .footer a {
            color: var(--primary-light);
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }

        /* ================= 10. 响应式设计 ================= */
        @media (max-width: 1024px) {
            .metrics-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .features-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .hero-title {
                font-size: 3rem;
            }
        }
        @media (max-width: 768px) {
            .metrics-grid {
                grid-template-columns: 1fr;
            }
            .features-grid {
                grid-template-columns: 1fr;
            }
            .chain-visual {
                flex-direction: column;
            }
            .hero-title {
                font-size: 2.5rem;
            }
            .workflow-container {
                flex-direction: column;
            }
        }
        
    </style>
    """, unsafe_allow_html=True)


def apply_console_css():
    """
    控制台模式 CSS：专业金融科技风格
    特点：深色主题、数据友好、专业感
    """
    st.markdown("""
    <style>
        /* 恢复侧边栏和顶部 */
        div[data-testid="stSidebar"] {display: block;}
        header[data-testid="stHeader"] {visibility: visible;}
        
        :root {
            --primary-color: #2563EB;
            --primary-light: #3B82F6;
            --accent-cyan: #06B6D4;
            --accent-green: #10B981;
            --bg-dark: #0A0F1C;
            --bg-card: #111827;
            --bg-card-hover: #1F2937;
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --border-color: rgba(59, 130, 246, 0.2);
        }
        
        /* 控制台深色背景 */
        .stApp {
            background: linear-gradient(180deg, #0A0F1C 0%, #111827 100%);
            color: var(--text-primary);
        }
        
        /* 侧边栏样式优化 */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
            border-right: 1px solid var(--border-color);
        }
        section[data-testid="stSidebar"] .stMarkdown {
            color: var(--text-primary);
        }
        section[data-testid="stSidebar"] label {
            color: var(--text-secondary) !important;
        }
        
        /* 输入框样式 */
        .stTextInput input, .stSelectbox select, .stTextArea textarea {
            background-color: var(--bg-card) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }
        .stTextInput input:focus, .stSelectbox select:focus {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
        }
        
        /* 按钮样式 */
        .stButton button {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-cyan)) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
        }
        
        /* 下载按钮特殊样式 */
        .stDownloadButton button {
            background: linear-gradient(135deg, var(--accent-green), #059669) !important;
        }
        
        /* 卡片/容器样式 */
        .stExpander {
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
        }
        
        /* 表格样式 */
        .stDataFrame {
            background-color: var(--bg-card) !important;
            border-radius: 12px !important;
        }
        
        /* 进度条样式 */
        .stProgress > div > div {
            background: linear-gradient(90deg, var(--primary-color), var(--accent-cyan)) !important;
        }
        
        /* 标签页样式 */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--bg-card);
            border-radius: 12px;
            padding: 0.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            color: var(--text-secondary);
            border-radius: 8px;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-cyan)) !important;
            color: white !important;
        }
        
        /* 成功/警告/错误消息 */
        .stSuccess {
            background-color: rgba(16, 185, 129, 0.1) !important;
            border: 1px solid rgba(16, 185, 129, 0.3) !important;
        }
        .stWarning {
            background-color: rgba(245, 158, 11, 0.1) !important;
            border: 1px solid rgba(245, 158, 11, 0.3) !important;
        }
        .stError {
            background-color: rgba(239, 68, 68, 0.1) !important;
            border: 1px solid rgba(239, 68, 68, 0.3) !important;
        }
        
        /* 标题样式 */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
        }
        
        /* 分割线 */
        hr {
            border-color: var(--border-color) !important;
        }
        
        /* 代码块 */
        code {
            background-color: var(--bg-card) !important;
            color: var(--accent-cyan) !important;
            padding: 0.2rem 0.4rem !important;
            border-radius: 4px !important;
        }
        
        /* 滚动条样式 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-dark);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-color);
        }
        
        /* 控制台头部 */
        .console-header {
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #06B6D4 100%);
            color: white;
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
        }
        .console-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.5;
        }
        .console-header h1 {
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
            position: relative;
            z-index: 1;
        }
        .console-header p {
            margin: 0.5rem 0 0;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        
        /* 状态指示器 */
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: var(--bg-card);
            border-radius: 20px;
            font-size: 0.875rem;
        }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        .status-dot.online {
            background: var(--accent-green);
            box-shadow: 0 0 10px var(--accent-green);
        }
        .status-dot.offline {
            background: var(--accent-red);
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* 研报卡片 */
        .report-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        .report-card:hover {
            border-color: var(--primary-color);
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.2);
        }
        .report-card h4 {
            margin: 0 0 0.5rem;
            color: var(--text-primary);
        }
        .report-card p {
            margin: 0;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }
        .report-card .meta {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
            font-size: 0.75rem;
            color: var(--text-muted);
        }
        
    </style>
    """, unsafe_allow_html=True)


def apply_report_viewer_css():
    """
    研报查看器专用CSS
    优化Markdown渲染效果
    """
    st.markdown("""
    <style>
        /* 研报内容区域 */
        .report-content {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 2rem;
            max-height: 70vh;
            overflow-y: auto;
        }
        
        .report-content h1 {
            font-size: 2rem;
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 0.5rem;
            margin-bottom: 1.5rem;
        }
        
        .report-content h2 {
            font-size: 1.5rem;
            color: var(--primary-light);
            margin-top: 2rem;
        }
        
        .report-content h3 {
            font-size: 1.25rem;
            color: var(--accent-cyan);
        }
        
        .report-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            background: var(--bg-card-hover);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .report-content th {
            background: linear-gradient(135deg, var(--primary-color), var(--accent-cyan));
            color: white;
            padding: 0.75rem 1rem;
            text-align: left;
            font-weight: 600;
        }
        
        .report-content td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid var(--border-color);
        }
        
        .report-content tr:hover {
            background: rgba(59, 130, 246, 0.1);
        }
        
        .report-content blockquote {
            border-left: 4px solid var(--primary-color);
            padding-left: 1rem;
            margin: 1rem 0;
            color: var(--text-secondary);
            background: rgba(59, 130, 246, 0.05);
            padding: 1rem;
            border-radius: 0 8px 8px 0;
        }
        
        .report-content code {
            background: var(--bg-dark);
            color: var(--accent-cyan);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
        }
        
        .report-content ul, .report-content ol {
            padding-left: 1.5rem;
        }
        
        .report-content li {
            margin-bottom: 0.5rem;
            line-height: 1.6;
        }
        
        .report-content strong {
            color: var(--accent-cyan);
        }
        
        .report-content a {
            color: var(--primary-light);
            text-decoration: none;
        }
        
        .report-content a:hover {
            text-decoration: underline;
        }
    </style>
    """, unsafe_allow_html=True)


def get_custom_theme():
    """
    返回自定义主题配置
    可用于Plotly等图表库
    """
    return {
        "colors": {
            "primary": "#2563EB",
            "secondary": "#06B6D4",
            "success": "#10B981",
            "warning": "#F59E0B",
            "danger": "#EF4444",
            "background": "#111827",
            "surface": "#1F2937",
            "text": "#F8FAFC",
            "text_secondary": "#94A3B8"
        },
        "fonts": {
            "primary": "Inter, sans-serif",
            "mono": "JetBrains Mono, monospace"
        },
        "chart_colors": [
            "#3B82F6", "#06B6D4", "#10B981", "#F59E0B", 
            "#EF4444", "#8B5CF6", "#EC4899", "#14B8A6"
        ]
    }
