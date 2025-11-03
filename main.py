import streamlit as st
import pandas as pd
import time
import threading
from functools import wraps
from src import data_fetcher, equity_analysis, technical_analysis, derivatives, news_feed, reports, portfolio_analysis, risk_analysis

# Caching and Performance Functions
@st.cache_data(ttl=3600)  # Cache for 1 hour
def cached_fetch_historical_data(symbol, years=5):
    """Cached version of historical data fetching"""
    return data_fetcher.fetch_historical_data(symbol, years)

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def cached_fetch_financial_statements(symbol):
    """Cached version of financial statements fetching"""
    return data_fetcher.fetch_financial_statements(symbol)

@st.cache_data(ttl=900)  # Cache for 15 minutes
def cached_fetch_asset_data(symbol, asset_class=None, period="1y", interval="1d"):
    """Cached version of asset data fetching"""
    return data_fetcher.fetch_asset_data(symbol, asset_class, period, interval)

def loading_spinner(text="Loading..."):
    """Decorator for functions that need loading indicators"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with st.spinner(text):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def background_task(func):
    """Decorator to run functions in background threads"""
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper

# Background Processing Functions
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_data_status():
    """Get status of cached data availability"""
    try:
        # Check if we have any cached data
        cache_info = st.session_state.get('cache_info', {})
        return {
            'has_historical_data': bool(cache_info.get('historical_data_last_update')),
            'has_financial_statements': bool(cache_info.get('financial_statements_last_update')),
            'last_update': cache_info.get('last_update'),
            'cache_size': len(cache_info)
        }
    except:
        return {'has_historical_data': False, 'has_financial_statements': False, 'last_update': None, 'cache_size': 0}

def lazy_load_data(symbol, data_type='historical', period='1y'):
    """Lazy loading function for data with background processing"""
    @background_task
    def load_in_background():
        try:
            with st.spinner(f"Loading {data_type} data for {symbol}..."):
                if data_type == 'historical':
                    data = cached_fetch_historical_data(symbol, years=5)
                elif data_type == 'financial':
                    data = cached_fetch_financial_statements(symbol)
                else:
                    data = cached_fetch_asset_data(symbol, period=period)

                # Store in session state for immediate access
                if 'lazy_loaded_data' not in st.session_state:
                    st.session_state.lazy_loaded_data = {}
                st.session_state.lazy_loaded_data[f"{symbol}_{data_type}"] = {
                    'data': data,
                    'timestamp': time.time(),
                    'status': 'loaded'
                }
                return data
        except Exception as e:
            handle_api_error(e, f"lazy loading {data_type} data for {symbol}")
            return None

    return load_in_background()

def get_lazy_loaded_data(symbol, data_type='historical'):
    """Retrieve lazy loaded data if available"""
    key = f"{symbol}_{data_type}"
    if 'lazy_loaded_data' in st.session_state and key in st.session_state.lazy_loaded_data:
        data_info = st.session_state.lazy_loaded_data[key]
        # Check if data is still fresh (within 30 minutes)
        if time.time() - data_info['timestamp'] < 1800:
            return data_info['data']
    return None

# Offline Mode Functions
def enable_offline_mode():
    """Enable offline mode with cached data"""
    if 'offline_mode' not in st.session_state:
        st.session_state.offline_mode = False

    cache_status = get_cached_data_status()
    if cache_status['cache_size'] > 0:
        st.session_state.offline_mode = True
        st.success("✅ Offline mode enabled! Using cached data.")
        return True
    else:
        st.warning("⚠️ No cached data available. Cannot enable offline mode.")
        return False

def disable_offline_mode():
    """Disable offline mode"""
    st.session_state.offline_mode = False
    st.info("🔄 Offline mode disabled. Using live data.")

def is_offline_mode():
    """Check if offline mode is enabled"""
    return st.session_state.get('offline_mode', False)

# Error Handling Functions
def handle_api_error(error, context=""):
    """Centralized error handling for API failures"""
    error_msg = f"Error {context}: {str(error)}"
    st.error(f"⚠️ {error_msg}")

    # Log error for debugging
    st.session_state.setdefault('error_log', []).append({
        'timestamp': time.time(),
        'error': error_msg,
        'context': context
    })

    return None

def retry_api_call(func, max_retries=3, delay=1):
    """Retry mechanism for API calls"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))  # Exponential backoff
    return None

# Cosmic Theme Configuration with Enhanced UI
st.set_page_config(
    page_title="Cosmic Financial Analysis by Innovate, Designed by Shikher",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply theme based on session state
current_theme = st.session_state.get('theme', 'dark')

# Define CSS variables based on current theme
if current_theme == 'light':
    css_variables = """
    :root {
        --bg-primary: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 50%, #dee2e6 100%);
        --bg-secondary: rgba(248, 249, 250, 0.95);
        --bg-tertiary: rgba(0, 0, 0, 0.05);
        --bg-card: rgba(0, 0, 0, 0.08);
        --text-primary: #212529;
        --text-secondary: #6c757d;
        --text-accent: #20c997;
        --border-primary: rgba(0, 0, 0, 0.1);
        --border-accent: rgba(32, 201, 151, 0.3);
        --shadow-primary: rgba(0, 0, 0, 0.1);
        --shadow-accent: rgba(32, 201, 151, 0.3);
        --gradient-primary: linear-gradient(45deg, #20c997, #007bff);
        --gradient-hover: linear-gradient(45deg, #17a2b8, #0056b3);
    }
    """
else:
    css_variables = """
    :root {
        --bg-primary: linear-gradient(180deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        --bg-secondary: rgba(26, 26, 46, 0.95);
        --bg-tertiary: rgba(255, 255, 255, 0.05);
        --bg-card: rgba(255, 255, 255, 0.08);
        --text-primary: #ffffff;
        --text-secondary: #cccccc;
        --text-accent: #4ecdc4;
        --border-primary: rgba(255, 255, 255, 0.1);
        --border-accent: rgba(255, 107, 107, 0.3);
        --shadow-primary: rgba(0, 0, 0, 0.3);
        --shadow-accent: rgba(255, 107, 107, 0.3);
        --gradient-primary: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        --gradient-hover: linear-gradient(45deg, #ff5252, #45b7aa);
    }
    """

# Enhanced Custom CSS for Cosmic Space Theme with Modern UI Elements and Theme Variables
st.markdown(f"""
<style>
    /* CSS Variables for Theme Support */
    {css_variables}

    /* Space background with animated stars */
    .main {{
        background: var(--bg-primary);
        background-attachment: fixed;
        color: var(--text-primary);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }}

    .main::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image:
            radial-gradient(2px 2px at 20px 30px, #eee, transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(255,255,255,0.8), transparent),
            radial-gradient(1px 1px at 90px 40px, #fff, transparent),
            radial-gradient(1px 1px at 130px 80px, rgba(255,255,255,0.6), transparent),
            radial-gradient(2px 2px at 160px 30px, #ddd, transparent);
        background-repeat: repeat;
        background-size: 200px 100px;
        animation: twinkle 4s ease-in-out infinite alternate;
        z-index: -1;
    }}

    /* Animated planets */
    .main::after {{
        content: '';
        position: fixed;
        top: 20%;
        right: 10%;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, #4a90e2 30%, #357abd 70%, transparent);
        border-radius: 50%;
        box-shadow: 0 0 20px rgba(74, 144, 226, 0.5);
        animation: orbit 20s linear infinite;
        z-index: -1;
    }}

    /* Enhanced sidebar styling */
    .css-1d391kg, .css-12oz5g7 {{
        background: rgba(26, 26, 46, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}

    /* Sidebar navigation buttons */
    .sidebar-nav-btn {{
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        padding: 12px 20px !important;
        margin: 5px 0 !important;
        width: 100% !important;
        text-align: left !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
    }}

    .sidebar-nav-btn:hover {{
        background: rgba(255, 107, 107, 0.2) !important;
        border-color: rgba(255, 107, 107, 0.3) !important;
        transform: translateX(5px) !important;
    }}

    .sidebar-nav-btn.active {{
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4) !important;
        border-color: rgba(255, 107, 107, 0.5) !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3) !important;
    }}

    /* Button styling */
    .stButton>button {{
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 15px 30px;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}

    .stButton>button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }}

    .stButton>button:hover::before {{
        left: 100%;
    }}

    .stButton>button:hover {{
        background: linear-gradient(45deg, #ff5252, #45b7aa);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
    }}

    /* Module cards */
    .module-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }}

    .module-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        border-color: rgba(255, 107, 107, 0.3);
    }}

    /* Dashboard metrics */
    .metric-card {{
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }}

    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
    }}

    .metric-value {{
        font-size: 2.5em;
        font-weight: bold;
        color: #4ecdc4;
        text-shadow: 0 0 10px rgba(78, 205, 196, 0.5);
    }}

    .metric-label {{
        font-size: 1.1em;
        color: #cccccc;
        margin-top: 10px;
    }}

    /* Search and filter components */
    .search-container {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 25px;
        padding: 15px 25px;
        margin: 20px 0;
        backdrop-filter: blur(10px);
    }}

    /* Animations */
    @keyframes twinkle {{
        0% {{ opacity: 0.3; }}
        100% {{ opacity: 1; }}
    }}

    @keyframes orbit {{
        0% {{ transform: rotate(0deg) translateX(50px) rotate(0deg); }}
        100% {{ transform: rotate(360deg) translateX(50px) rotate(-360deg); }}
    }}

    /* Text styling */
    h1, h2, h3 {{
        color: #ffffff !important;
        text-shadow: 0 0 10px rgba(255, 107, 107, 0.5);
    }}

    /* Dataframe styling */
    .dataframe {{
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}

    /* Metric styling */
    .metric-container {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    /* Loading spinner */
    .loading-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }}

    .spinner {{
        width: 50px;
        height: 50px;
        border: 3px solid rgba(255, 255, 255, 0.1);
        border-top: 3px solid #4ecdc4;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }}

    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: rgba(255, 255, 255, 0.1);
    }}

    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(45deg, #ff5252, #45b7aa);
    }}

    /* Mobile responsiveness */
    @media (max-width: 768px) {{
        .metric-card {{
            margin: 10px 0;
            padding: 15px;
        }}

        .metric-value {{
            font-size: 2em;
        }}

        .sidebar-nav-btn {{
            padding: 10px 15px !important;
            font-size: 14px !important;
        }}

        /* Mobile sidebar improvements */
        .css-1d391kg, .css-12oz5g7 {{
            width: 280px !important;
        }}

        /* Mobile search interface */
        .search-container {{
            padding: 10px 15px;
            margin: 15px 0;
        }}

        /* Mobile favorites grid */
        .favorites-grid {{
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)) !important;
            gap: 15px !important;
        }}

        /* Mobile metric cards in search results */
        .search-result-card {{
            padding: 15px !important;
            margin: 10px 0 !important;
        }}

        /* Mobile button sizing */
        .stButton>button {{
            padding: 12px 20px !important;
            font-size: 14px !important;
            width: 100% !important;
            margin: 5px 0 !important;
        }}

        /* Mobile chart responsiveness */
        .stLineChart {{
            height: 250px !important;
        }}

        /* Mobile column layouts */
        .mobile-col-2 {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .mobile-col-2 > div {{
            width: 100% !important;
        }}

        /* Mobile popular searches */
        .popular-searches {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
        }}

        .popular-searches button {{
            padding: 8px 12px !important;
            font-size: 12px !important;
        }}

        /* Mobile related assets */
        .related-assets {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }}

        .related-assets button {{
            padding: 8px 12px !important;
            font-size: 12px !important;
        }}

        /* Mobile dashboard metrics */
        .dashboard-metrics {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}

        .dashboard-metrics .metric-card {{
            text-align: center;
        }}

        /* Mobile feature overview */
        .feature-overview {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
        }}

        /* Mobile quick actions */
        .quick-actions {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
        }}

        /* Mobile favorites display */
        .favorites-display {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
        }}

        /* Mobile module cards */
        .module-card {{
            padding: 20px !important;
            margin: 15px 0 !important;
        }}

        /* Mobile text sizing */
        h1 {{
            font-size: 1.8em !important;
        }}

        h2 {{
            font-size: 1.5em !important;
        }}

        h3 {{
            font-size: 1.3em !important;
        }}

        /* Mobile spacing adjustments */
        .stMarkdown {{
            margin-bottom: 15px !important;
        }}

        /* Mobile input fields */
        .stTextInput input {{
            font-size: 16px !important; /* Prevents zoom on iOS */
        }}

        .stSelectbox select {{
            font-size: 16px !important;
        }}

        /* Mobile dataframes */
        .dataframe {{
            font-size: 12px !important;
            overflow-x: auto !important;
        }}

        /* Mobile metric containers */
        .metric-container {{
            padding: 15px !important;
            margin: 10px 0 !important;
        }}
    }}

    /* Tablet responsiveness */
    @media (max-width: 1024px) and (min-width: 769px) {{
        .dashboard-metrics {{
            grid-template-columns: repeat(2, 1fr);
        }}

        .feature-overview {{
            grid-template-columns: repeat(2, 1fr);
        }}

        .favorites-display {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}
</style>
""", unsafe_allow_html=True)

# Main App with Enhanced Sidebar Navigation
def main():
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;">
            <h2 style="color: #4ecdc4; margin: 0; font-size: 1.5em;">🌌 Cosmic FA</h2>
            <p style="color: #cccccc; font-size: 0.8em; margin: 5px 0;">Financial Analysis</p>
        </div>
        """, unsafe_allow_html=True)

        # Navigation Menu
        st.markdown("### 📱 Navigation")

        # Home/Dashboard
        if st.button("🏠 Dashboard", key="nav_home", help="Main dashboard and overview"):
            st.session_state.selected_module = "Home"

        # Data & Analysis Modules
        st.markdown("### 📊 Analysis Modules")

        nav_buttons = [
            ("📈 Data Fetching", "Data Fetching", "Fetch and analyze financial data"),
            ("📊 Equity Analysis", "Equity Analysis", "Analyze equity markets and stocks"),
            ("💹 Derivatives/Forex/Crypto", "Derivatives/Forex/Crypto", "Analyze derivatives, forex, and crypto"),
            ("📰 News Feed", "News Feed", "Latest financial news and updates"),
            ("📊 Portfolio Analysis", "Portfolio Analysis", "Multi-asset portfolio analysis"),
            ("⚠️ Risk Analysis", "Risk Analysis", "Risk assessment and management"),
            ("📋 Reports", "Reports", "Generate financial reports")
        ]

        for label, module, help_text in nav_buttons:
            if st.button(label, key=f"nav_{module.lower().replace(' ', '_')}", help=help_text):
                st.session_state.selected_module = module

        # Settings & Tools
        st.markdown("### ⚙️ Tools")
        if st.button("🔍 Search Assets", key="nav_search", help="Search for financial assets"):
            st.session_state.selected_module = "Search"

        if st.button("⭐ Favorites", key="nav_favorites", help="View favorite assets"):
            st.session_state.selected_module = "Favorites"

        # Theme Toggle
        st.markdown("### 🎨 Theme")
        current_theme = st.session_state.get('theme', 'dark')
        theme_icon = "🌙" if current_theme == "dark" else "☀️"
        theme_text = "Dark Mode" if current_theme == "dark" else "Light Mode"
        toggle_text = f"{theme_icon} Switch to {'Light' if current_theme == 'dark' else 'Dark'} Mode"

        if st.button(toggle_text, key="theme_toggle", help=f"Currently in {theme_text}"):
            new_theme = "light" if current_theme == "dark" else "dark"
            st.session_state.theme = new_theme
            st.rerun()

        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 10px; color: #666;">
            <small>© 2024<br>Designed by Shikher</small>
        </div>
        """, unsafe_allow_html=True)

    # Main Content Area
    st.title("🌌 Cosmic Financial Analysis")
    st.markdown("### Advanced Financial Modeling & Analysis for Indian Markets")

    # Copyright Warning
    st.warning("⚠️ **IMPORTANT NOTICE:** This software is patented and copyrighted. Any unauthorized copying, distribution, or modification of this software will result in severe legal consequences. This software is protected under intellectual property laws.")

    # Module Content Display
    selected_module = st.session_state.get('selected_module', 'Home')

    if selected_module == "Home":
        # Enhanced Home Dashboard
        st.markdown("## 🏠 Dashboard Overview")

        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">8</div>
                <div class="metric-label">Analysis Modules</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">6</div>
                <div class="metric-label">Asset Classes</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">∞</div>
                <div class="metric-label">Data Sources</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">₹</div>
                <div class="metric-label">INR Focused</div>
            </div>
            """, unsafe_allow_html=True)

        # Welcome Section
        st.markdown("""
        <div class="module-card">
            <h3 style="text-align: center; color: #ffffff;">Welcome to Cosmic Financial Analyzer</h3>
            <p style="text-align: center; color: #cccccc; font-size: 18px;">
                Your comprehensive platform for advanced financial analysis and modeling in the Indian market context
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Quick Actions
        st.markdown("## 🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Start Data Analysis", key="quick_data", use_container_width=True):
                st.session_state.selected_module = "Data Fetching"

        with col2:
            if st.button("📈 Analyze Portfolio", key="quick_portfolio", use_container_width=True):
                st.session_state.selected_module = "Portfolio Analysis"

        with col3:
            if st.button("⚠️ Risk Assessment", key="quick_risk", use_container_width=True):
                st.session_state.selected_module = "Risk Analysis"

        # Feature Overview
        st.markdown("## ✨ Key Features")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="module-card">
                <h4>📊 Multi-Source Data</h4>
                <p>Fetch and analyze financial data from Yahoo Finance, Alpha Vantage, and other reliable sources with automatic INR conversion.</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="module-card">
                <h4>📈 Advanced Analytics</h4>
                <p>Technical indicators, risk metrics, portfolio optimization, and comprehensive financial statement analysis.</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="module-card">
                <h4>💼 Portfolio Management</h4>
                <p>Multi-asset portfolio tracking, rebalancing, performance analysis, and risk management tools.</p>
            </div>
            """, unsafe_allow_html=True)

    elif selected_module == "Search":
        st.markdown("## 🔍 Asset Search")

        # Initialize favorites in session state if not exists
        if 'favorites' not in st.session_state:
            st.session_state.favorites = set()

        # Search interface
        col1, col2 = st.columns([3, 1])

        with col1:
            search_query = st.text_input(
                "Search for stocks, crypto, commodities, etc.",
                placeholder="e.g., AAPL, BTC, GOLD, RELIANCE.NS",
                key="search_query"
            )

        with col2:
            asset_class_filter = st.selectbox(
                "Filter by Asset Class",
                ["All", "Equity", "Cryptocurrency", "Commodities", "Bonds", "ETF", "Forex"],
                key="asset_class_filter"
            )

        # Popular searches
        st.markdown("### 🔥 Popular Searches")
        popular_searches = [
            "AAPL", "BTC", "GOLD", "RELIANCE.NS", "USDINR=X",
            "MSFT", "ETH", "SILVER", "TCS.NS", "SPY"
        ]

        cols = st.columns(5)
        for i, symbol in enumerate(popular_searches):
            with cols[i % 5]:
                if st.button(symbol, key=f"popular_{symbol}", use_container_width=True):
                    st.session_state.search_query = symbol
                    st.rerun()

        # Search results
        if search_query:
            st.markdown(f"### Search Results for '{search_query}'")

            # Detect asset class
            detected_class = data_fetcher.detect_asset_class(search_query.upper())

            # Filter check
            if asset_class_filter != "All" and detected_class != asset_class_filter:
                st.warning(f"⚠️ '{search_query}' appears to be {detected_class}, but you're filtering for {asset_class_filter}")
                if not st.checkbox("Show anyway"):
                    st.stop()

            # Asset info card
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{search_query.upper()}</h4>
                    <p style="color: #4ecdc4; font-size: 18px;">{detected_class}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                is_favorite = search_query.upper() in st.session_state.favorites
                if st.button(
                    "⭐" if is_favorite else "☆",
                    key=f"fav_{search_query}",
                    help="Add to favorites" if not is_favorite else "Remove from favorites"
                ):
                    if is_favorite:
                        st.session_state.favorites.remove(search_query.upper())
                        st.success(f"Removed {search_query.upper()} from favorites")
                    else:
                        st.session_state.favorites.add(search_query.upper())
                        st.success(f"Added {search_query.upper()} to favorites")

            with col3:
                if st.button("📊 Analyze", key=f"analyze_{search_query}", use_container_width=True):
                    # Set data fetcher to this symbol
                    st.session_state.selected_symbol = search_query.upper()
                    st.session_state.selected_module = "Data Fetching"
                    st.rerun()

            # Try to fetch basic data with caching and error handling
            try:
                data = retry_api_call(lambda: cached_fetch_asset_data(search_query.upper(), period='1mo'))

                if data is not None and not data.empty:
                    # Current price
                    current_price = data['Close'].iloc[-1] if 'Close' in data.columns else "N/A"

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Current Price", f"₹{current_price:,.2f}" if isinstance(current_price, (int, float)) else current_price)

                    with col2:
                        change = data['Close'].iloc[-1] - data['Close'].iloc[-2] if len(data) > 1 else 0
                        change_pct = (change / data['Close'].iloc[-2]) * 100 if len(data) > 1 and data['Close'].iloc[-2] != 0 else 0
                        st.metric("Change", f"₹{change:+,.2f}", f"{change_pct:+.2f}%")

                    with col3:
                        volume = data['Volume'].iloc[-1] if 'Volume' in data.columns else "N/A"
                        st.metric("Volume", f"{volume:,.0f}" if isinstance(volume, (int, float)) else volume)

                    # Quick chart
                    st.markdown("### 📈 Recent Performance")
                    st.line_chart(data['Close'])

                    # Export options
                    st.markdown("### 💾 Export Data")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("📊 CSV", key=f"export_csv_{search_query}", use_container_width=True):
                            csv_data = data.to_csv(index=True)
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name=f"{search_query.upper()}_data.csv",
                                mime="text/csv",
                                key=f"download_csv_{search_query}"
                            )

                    with col2:
                        if st.button("📈 Excel", key=f"export_excel_{search_query}", use_container_width=True):
                            # Convert to Excel format (simplified)
                            excel_data = data.to_csv(index=True)
                            st.download_button(
                                label="Download Excel",
                                data=excel_data,
                                file_name=f"{search_query.upper()}_data.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"download_excel_{search_query}"
                            )

                    with col3:
                        if st.button("📋 JSON", key=f"export_json_{search_query}", use_container_width=True):
                            json_data = data.to_json(orient='records', date_format='iso')
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f"{search_query.upper()}_data.json",
                                mime="application/json",
                                key=f"download_json_{search_query}"
                            )

                else:
                    st.warning("Unable to fetch data for this symbol. It may be invalid or temporarily unavailable.")

            except Exception as e:
                handle_api_error(e, f"fetching data for {search_query}")

            # Related assets suggestions
            st.markdown("### 💡 Related Assets")
            asset_suggestions = {
                "Equity": ["AAPL", "MSFT", "GOOGL", "TSLA", "RELIANCE.NS", "TCS.NS"],
                "Cryptocurrency": ["BTC", "ETH", "BNB", "ADA", "SOL", "DOT"],
                "Commodities": ["GOLD", "SILVER", "OIL", "COPPER", "NATURAL_GAS", "PLATINUM"],
                "Bonds": ["US10Y", "US30Y", "US5Y", "US2Y", "US3M", "DE10Y"],
                "ETF": ["SPY", "QQQ", "VTI", "VEA", "VWO", "BND"],
                "Forex": ["USDINR=X", "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"]
            }

            if detected_class in asset_suggestions:
                suggestions = [s for s in asset_suggestions[detected_class] if s != search_query.upper()][:4]
                if suggestions:
                    cols = st.columns(4)
                    for i, suggestion in enumerate(suggestions):
                        with cols[i]:
                            if st.button(suggestion, key=f"suggest_{suggestion}", use_container_width=True):
                                st.session_state.search_query = suggestion
                                st.rerun()

    elif selected_module == "Favorites":
        st.markdown("## ⭐ Favorite Assets")

        if not st.session_state.favorites:
            st.info("No favorite assets yet. Search for assets and add them to your favorites using the ⭐ button.")

            # Quick add popular assets
            st.markdown("### 🚀 Quick Add Popular Assets")
            popular_assets = [
                ("AAPL", "Equity"), ("BTC", "Cryptocurrency"), ("GOLD", "Commodities"),
                ("SPY", "ETF"), ("USDINR=X", "Forex"), ("RELIANCE.NS", "Equity")
            ]

            cols = st.columns(3)
            for i, (symbol, asset_class) in enumerate(popular_assets):
                with cols[i % 3]:
                    if st.button(f"⭐ {symbol} ({asset_class})", key=f"quick_add_{symbol}", use_container_width=True):
                        st.session_state.favorites.add(symbol)
                        st.success(f"Added {symbol} to favorites!")
                        st.rerun()

        else:
            st.success(f"You have {len(st.session_state.favorites)} favorite assets")

            # Favorites grid
            favorites_list = list(st.session_state.favorites)
            cols = st.columns(3)

            for i, symbol in enumerate(favorites_list):
                with cols[i % 3]:
                    try:
                        # Quick data fetch for display
                        data = data_fetcher.fetch_asset_data(symbol, period='1d')
                        current_price = data['Close'].iloc[-1] if data is not None and not data.empty and 'Close' in data.columns else "N/A"

                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>{symbol}</h4>
                            <p style="color: #4ecdc4; font-size: 18px;">₹{current_price:,.2f}</p>
                            <small style="color: #cccccc;">{data_fetcher.detect_asset_class(symbol)}</small>
                        </div>
                        """, unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📊 Analyze", key=f"fav_analyze_{symbol}", use_container_width=True):
                                st.session_state.selected_symbol = symbol
                                st.session_state.selected_module = "Data Fetching"
                                st.rerun()

                        with col2:
                            if st.button("❌ Remove", key=f"fav_remove_{symbol}", use_container_width=True):
                                st.session_state.favorites.remove(symbol)
                                st.success(f"Removed {symbol} from favorites")
                                st.rerun()

                    except Exception as e:
                        st.error(f"Error loading {symbol}: {str(e)}")

            # Clear all favorites
            if st.button("🗑️ Clear All Favorites", key="clear_favorites"):
                st.session_state.favorites.clear()
                st.success("All favorites cleared!")
                st.rerun()

    elif selected_module == "Data Fetching":
        data_fetcher.display()

    elif selected_module == "Equity Analysis":
        equity_analysis.display()

    elif selected_module == "Derivatives/Forex/Crypto":
        derivatives.display()

    elif selected_module == "News Feed":
        news_feed.display()

    elif selected_module == "Portfolio Analysis":
        portfolio_analysis.display()

    elif selected_module == "Risk Analysis":
        risk_analysis.display()

    elif selected_module == "Reports":
        reports.display()

if __name__ == "__main__":
    main()
