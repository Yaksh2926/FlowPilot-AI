import streamlit as st

# Set Streamlit Page Configuration BEFORE importing any page modules
st.set_page_config(
    page_title="FlowPilot AI - One Agent to Rule Them All",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

import time
from style import inject_custom_css
from utils import initialize_mock_data
from chat import render_chat_page
from crm import render_crm_page
from RAG import render_rag_page
from workflows import render_workflows_page
from dashboard import render_dashboard_page
from admin import render_admin_page

# 1. Initialize State & Custom Styles
initialize_mock_data()
inject_custom_css()

# 2. Sidebar Navigation Layout
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 1.5rem; padding: 10px 0;">
        <div style="
            display: inline-block;
            background: linear-gradient(135deg, #6366f1 0%, #38bdf8 100%);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            line-height: 50px;
            font-size: 1.6rem;
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.5);
            margin-bottom: 8px;
        ">
            🚀
        </div>
        <h2 style="
            margin: 0; 
            font-family: 'Outfit', sans-serif; 
            font-size: 1.6rem;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        ">
            FlowPilot AI
        </h2>
        <span style="font-size: 0.75rem; color: #94a3b8; letter-spacing: 0.1em; text-transform: uppercase;">
            Unified Operations Agent
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("### 🧭 Main Navigation")
menu_selection = st.sidebar.radio(
    "Go to workspace:",
    [
        "🤖 Customer Support Bot",
        "👥 CRM & Churn Predictor",
        "⚡ Automations & Webhooks",
        "📚 RAG Knowledge Base",
        "📊 Operational Analytics",
        "🛡️ Operations Desk Admin"
    ]
)

st.sidebar.markdown("---")

# 3. Sidebar API Key Config Section
st.sidebar.markdown("### 🔑 API Integrations")
gemini_key_input = st.sidebar.text_input(
    "Google AI Studio API Key",
    type="password",
    value=st.session_state.get("gemini_api_key", ""),
    placeholder="Starts with AIzaSy..."
)

if gemini_key_input:
    st.session_state.gemini_api_key = gemini_key_input
    if "api_verified" not in st.session_state:
        st.session_state.api_verified = True
        st.sidebar.success("✅ Gemini API Key Loaded! Live AI responses active (gemini-2.5-flash).")
        time.sleep(1)
        st.rerun()
else:
    st.session_state.gemini_api_key = ""
    st.sidebar.info("💡 Running in Simulation Mode. Enter your Google AI Studio API Key above to enable live Gemini responses.")

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="font-size: 0.75rem; color: #64748b; text-align: center; margin-top: 2rem;">
        FlowPilot AI • Hackathon Edition<br>
        Open Innovation Category 🏆
    </div>
    """,
    unsafe_allow_html=True
)

# 4. Page Routing Logic
if menu_selection == "🤖 Customer Support Bot":
    render_chat_page()
elif menu_selection == "👥 CRM & Churn Predictor":
    render_crm_page()
elif menu_selection == "⚡ Automations & Webhooks":
    render_workflows_page()
elif menu_selection == "📚 RAG Knowledge Base":
    render_rag_page()
elif menu_selection == "📊 Operational Analytics":
    render_dashboard_page()
elif menu_selection == "🛡️ Operations Desk Admin":
    render_admin_page()
