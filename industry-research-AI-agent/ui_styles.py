# investment_agent_crewai/ui_styles.py
import streamlit as st

def apply_landing_page_css():
    """
    官网模式专用 CSS：复刻 FinSight Showcase 风格
    特点：极简白底、卡片悬浮、大字体、隐藏原生侧边栏
    """
    st.markdown("""
    <style>
        /* ================= 1. 全局重置与字体 ================= */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        .stApp {
            background-color: #FFFFFF; /* 纯白底色 */
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* 隐藏 Streamlit 原生干扰元素 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {visibility: hidden;} /* 隐藏顶部彩条 */
        div[data-testid="stSidebar"] {display: none;} /* 强制隐藏侧边栏 */
        
        /* 调整页面边距，让内容更紧凑 */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 5rem !important;
            max-width: 1200px !important;
        }

        /* ================= 2. 导航栏 (Navbar) ================= */
        .nav-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem 0;
            margin-bottom: 3rem;
            border-bottom: 1px solid #F1F5F9;
        }
        .nav-logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: #0F172A;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .nav-badge {
            background: #EFF6FF;
            color: #3B82F6;
            font-size: 0.75rem;
            padding: 4px 8px;
            border-radius: 12px;
            font-weight: 600;
        }

        /* ================= 3. Hero 区域 (大标题) ================= */
        .hero-section {
            text-align: center;
            padding: 4rem 0 3rem 0;
        }
        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 1.5rem;
            color: #0F172A;
        }
        .hero-highlight {
            background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-subtitle {
            font-size: 1.25rem;
            color: #64748B;
            max-width: 800px;
            margin: 0 auto;
            line-height: 1.6;
        }

        /* ================= 4. 核心指标卡片 (Metrics) ================= */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
            margin: 3rem 0;
        }
        .metric-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px -10px rgba(0, 0, 0, 0.1);
            border-color: #3B82F6;
        }
        .metric-value {
            display: block;
            font-size: 2.25rem;
            font-weight: 800;
            color: #0F172A;
            margin-bottom: 0.5rem;
        }
        .metric-label {
            color: #64748B;
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* ================= 5. 内容区块通用样式 ================= */
        .section-title {
            font-size: 2rem;
            font-weight: 700;
            color: #0F172A;
            margin: 4rem 0 2rem 0;
            text-align: center;
        }
        
        /* 6维度卡片 grid */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
        }
        .feature-card {
            background: #F8FAFC;
            padding: 2rem;
            border-radius: 16px;
            border: 1px solid transparent;
            transition: all 0.2s;
        }
        .feature-card:hover {
            background: #FFFFFF;
            border-color: #E2E8F0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: #3B82F6;
        }
        .feature-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #0F172A;
            margin-bottom: 0.75rem;
        }
        .feature-desc {
            color: #64748B;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        /* ================= 6. 产业链可视化 (三色块) ================= */
        .chain-wrapper {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        }
        .chain-visual {
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
        }
        .chain-step {
            flex: 1;
            padding: 2rem;
            border-radius: 12px;
            color: white;
            position: relative;
            overflow: hidden;
        }
        .chain-step h3 { color: white !important; margin-top: 0; font-size: 1.25rem; }
        .chain-step p { opacity: 0.9; font-size: 0.9rem; margin-bottom: 0; }
        
        .bg-green { background: linear-gradient(135deg, #10B981 0%, #059669 100%); }
        .bg-blue { background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%); }
        .bg-orange { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); }

        /* ================= 7. 架构图 (Workflow) ================= */
        .workflow-container {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
            gap: 1rem;
            margin-top: 2rem;
        }
        .workflow-node {
            background: #EFF6FF;
            color: #1E40AF;
            padding: 0.75rem 1.5rem;
            border-radius: 99px;
            font-weight: 600;
            border: 1px solid #BFDBFE;
        }
        .workflow-arrow { color: #94A3B8; font-size: 1.2rem; }

        /* ================= 8. 自定义按钮样式 (覆盖 Streamlit 默认) ================= */
        /* 定位右上角的按钮 */
        div[data-testid="column"]:nth-of-type(2) button {
            background-color: #0F172A !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 600 !important;
            transition: opacity 0.2s;
        }
        div[data-testid="column"]:nth-of-type(2) button:hover {
            opacity: 0.9;
        }
        
    </style>
    """, unsafe_allow_html=True)


def apply_console_css():
    """
    控制台模式 CSS：恢复侧边栏，使用护眼配色
    """
    st.markdown("""
    <style>
        /* 恢复侧边栏和顶部 */
        div[data-testid="stSidebar"] {display: block;}
        header[data-testid="stHeader"] {visibility: visible;}
        
        /* 控制台背景微调 */
        .stApp {
            background-color: #F8FAFC;
        }
        
        /* 侧边栏样式优化 */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }
        
        /* 标题海浪动画容器 (保留你之前的特色) */
        .header-container {
            background: linear-gradient(120deg, #1E3A8A, #3B82F6);
            color: white;
            padding: 2rem;
            border-radius: 0 0 20px 20px;
            margin: -6rem -4rem 2rem -4rem; /* 抵消 padding */
            text-align: center;
            position: relative;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)

