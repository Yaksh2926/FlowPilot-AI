import streamlit as st

def inject_custom_css():
    """
    Injects custom CSS to style Streamlit for a premium, high-fidelity dark mode
    experience with glassmorphism, smooth animations, and custom font weights.
    """
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    /* General Body Styles */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', 'Inter', sans-serif;
        background-color: #0b0f19;
        color: #f3f4f6;
    }

    /* Sidebar Styles */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    [data-testid="stSidebar"] * {
        font-family: 'Outfit', sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Custom Header/Title Styles */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.025em;
    }

    h1 {
        font-size: 2.75rem !important;
        margin-bottom: 1.5rem !important;
    }

    h2 {
        font-size: 1.85rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
    }

    /* Glassmorphic Card Container */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
        transform: translateY(-2px);
    }

    /* Mini Dashboard Metrics styling */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.35);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 0.85rem 1.25rem !important;
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.2);
        transition: border-color 0.2s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        border-color: rgba(56, 189, 248, 0.25);
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        font-family: 'Outfit', sans-serif;
        color: #38bdf8 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8 !important;
    }

    /* Custom Gradient Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        font-family: 'Outfit', sans-serif !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5) !important;
        background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(1px) !important;
    }

    /* Form and Inputs Glass styling */
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #f3f4f6 !important;
    }
    
    /* Streamlit Chat Messages */
    [data-testid="stChatMessage"] {
        background: rgba(30, 41, 59, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    /* Hide Default Streamlit Menu / Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* Custom tags / statuses */
    .status-pill {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-positive {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-neutral {
        background-color: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .status-negative {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Scrollbar customization */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.25);
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def card(title, content_html):
    """
    Renders a premium glass-styled card.
    """
    st.markdown(
        f"""
        <div class="glass-card">
            <h4 style="margin-top:0; color:#38bdf8; font-family:'Outfit', sans-serif; font-size:1.15rem; margin-bottom: 0.5rem;">{title}</h4>
            <div>{content_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
