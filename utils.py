import streamlit as st
import pandas as pd
import numpy as np
import io
import time
import json
import os
from fpdf import FPDF

# --- Global AI Wrapper (Google Gemini via AI Studio) ---
def get_ai_client():
    """
    Returns a Gemini client if the API key is present in st.session_state or environment.
    Priority: session_state (sidebar input) > GEMINI_API_KEY env variable.
    """
    api_key = st.session_state.get("gemini_api_key", "") or os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        return client
    except Exception as e:
        st.sidebar.error(f"Error loading google-genai SDK: {e}")
        return None

def generate_ai_response(prompt, system_instruction=""):
    """
    Generates a response from the Gemini API (Google AI Studio) if a client is available.
    Otherwise, falls back to the rule-based simulation engine for demo mode.
    """
    client = get_ai_client()
    if client:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    'system_instruction': system_instruction,
                    'temperature': 0.7
                }
            )
            return response.text
        except Exception as e:
            return f"🤖 [Gemini API Error — falling back to simulation]: {e}\n\n" + simulate_fallback_response(prompt, system_instruction)
    else:
        # Simulate realistic response delays for demo fidelity
        time.sleep(0.6)
        return simulate_fallback_response(prompt, system_instruction)

def simulate_fallback_response(prompt, system_instruction):
    """
    Rule-based mock responder that matches key phrases for Sales, Support, and Customer Care.
    """
    p_lower = prompt.lower()
    role = "support"
    if "sales" in system_instruction.lower():
        role = "sales"
    elif "care" in system_instruction.lower() or "retention" in system_instruction.lower():
        role = "care"

    # Sales answers
    if role == "sales":
        if any(w in p_lower for w in ["price", "cost", "pricing", "plans"]):
            return "Our pricing starts at $49/month for the **Starter Plan** (up to 3 users), $149/month for the **Growth Plan** (up to 15 users, includes CRM integrations), and custom **Enterprise** solutions starting at $499/month. Which plan matches your team scale?"
        elif any(w in p_lower for w in ["demo", "trial", "try"]):
            return "I can absolutely set up a demo for you! We offer a 14-day free trial on all plans. Would you like to schedule a 15-minute walkthrough session with our success team tomorrow at 10 AM or 2 PM?"
        elif any(w in p_lower for w in ["discount", "deal", "promo"]):
            return "For our launch event this month, we're offering a 20% discount on annual subscriptions. Let me know if you'd like me to send you the voucher code directly to your email!"
        elif any(w in p_lower for w in ["feature", "what does it do", "capabilities"]):
            return "FlowPilot AI integrates Sales, Support, and Customer Care into one dashboard. It features live CRM tracking, instant multi-channel sync (Slack/Web/Email), voice synthesis, and automatic workflow generation. What specific workflow are you looking to optimize?"
        else:
            return "Thank you for showing interest in FlowPilot AI! We help teams consolidate their customer operations. I'd love to learn more about your business context. Are you looking to improve response times or increase sales conversions?"

    # Support answers
    elif role == "support":
        if any(w in p_lower for w in ["reset", "password", "login", "forgot"]):
            return "To reset your password, please go to the login screen and click **'Forgot Password'**. You will receive a secure token via email to create a new password. If you don't receive it within 5 minutes, let me know, and I can trigger a manual reset ticket for you."
        elif any(w in p_lower for w in ["slow", "bug", "crash", "error", "down"]):
            return "I am very sorry to hear that. I have analyzed our system status and logged this error. I can instantly generate a high-priority support ticket to our engineering team. Would you like me to create this ticket now?"
        elif any(w in p_lower for w in ["refund", "billing", "invoice"]):
            return "I've checked our billing console. To process refunds or invoice adjustments, I will escalate this to our finance desk. Let me open a Billing Support Ticket for you right away so they can look into this transaction."
        else:
            return "I've logged your query. Our support bot is scanning our FAQ library. Let me know if you would like me to create a support ticket or hand you off to a live representative for real-time troubleshooting."

    # Care / Retention answers
    else:
        if any(w in p_lower for w in ["cancel", "leave", "quit", "unsubscribe"]):
            return "We are sad to see you go! Before you make a decision, we would love to offer a free 1-on-1 optimization call with our Customer Success Manager. We can also apply a 30-day billing freeze to give you time to evaluate. What is the main blocker you are currently facing?"
        elif any(w in p_lower for w in ["upgrade", "expand", "more seats"]):
            return "That's fantastic! Upgrading your plan is simple. I have notified your Account Executive to send you the direct checkout link. Your data will sync automatically. Is there any particular onboarding help you need for the new team members?"
        else:
            return "Welcome back! I am here to help you get the most out of FlowPilot AI. I can review your usage data, check for any open concerns, or help you configure custom Slack notifications. What would you like to build today?"

# --- Sentiment Analyzer ---
def analyze_sentiment(text):
    """
    Performs sentiment analysis.
    Returns: (sentiment_label, score_0_to_1, color_class)
    """
    text_lower = text.lower()
    negative_words = ["bad", "slow", "error", "useless", "worst", "broken", "cancel", "frustrated", "hate", "issue", "bug", "fail", "terrible", "expensive"]
    positive_words = ["good", "great", "love", "amazing", "best", "helpful", "awesome", "perfect", "thanks", "thank you", "excel", "cool", "faster", "happy"]
    
    neg_count = sum(1 for w in negative_words if w in text_lower)
    pos_count = sum(1 for w in positive_words if w in text_lower)
    
    if neg_count > pos_count:
        score = min(0.5 + 0.1 * neg_count, 0.98)
        return "Negative", score, "status-negative"
    elif pos_count > neg_count:
        score = min(0.5 + 0.1 * pos_count, 0.98)
        return "Positive", score, "status-positive"
    else:
        return "Neutral", 0.75, "status-neutral"

# --- Explainable AI Logic ---
def get_explainable_ai_reason(prompt, response, role):
    """
    Explains 'why' the bot responded the way it did.
    """
    sentiment, score, _ = analyze_sentiment(prompt)
    if "price" in prompt.lower() or "cost" in prompt.lower():
        reason = f"Customer queried pricing. Match pattern: pricing intents. Sentiment is {sentiment} ({int(score*100)}%). System provided standard pricing tier details."
    elif "cancel" in prompt.lower() or "leave" in prompt.lower():
        reason = f"Customer indicated intent to cancel. Churn flags raised! Triggered Care Bot Customer Success playbooks. Offer applied: 1-on-1 review or 30-day freeze."
    elif "bug" in prompt.lower() or "error" in prompt.lower() or "slow" in prompt.lower():
        reason = f"System detected service disruption complaint. Escalated status internally. Prepared options for immediate support ticket generation (Support flow)."
    else:
        reason = f"Standard {role.capitalize()} Agent model evaluated prompt. Sentiment: {sentiment}. Triggered general conversational model to outline value proposition."
    return reason

# --- Churn Prediction Simulator ---
def predict_churn_risk(row):
    """
    Simulates a machine learning prediction score.
    Returns risk percentage (0 to 100).
    """
    base_risk = 15.0
    
    # Factor 1: Open Tickets (more open tickets = higher risk)
    open_t = row.get("open_tickets", 0)
    base_risk += open_t * 15.0
    
    # Factor 2: Customer Sentiment
    sent = row.get("recent_sentiment", "Neutral")
    if sent == "Negative":
        base_risk += 35.0
    elif sent == "Positive":
        base_risk -= 10.0
        
    # Factor 3: Total Spend
    spend = row.get("total_spend", 500)
    if spend > 2000:
        base_risk -= 8.0
        
    # Factor 4: Tenure (Days active, shorter tenure = higher churn risk)
    tenure = row.get("tenure_days", 100)
    if tenure < 30:
        base_risk += 12.0
    elif tenure > 180:
        base_risk -= 10.0
        
    # Clamp to [2, 98]
    return float(np.clip(base_risk, 2.0, 98.0))

# --- Dummy Data Generator ---
def initialize_mock_data():
    """
    Initializes mock session data.
    """
    if "crm_data" not in st.session_state:
        st.session_state.crm_data = pd.DataFrame([
            {"customer_id": "C-101", "name": "Sarah Connor", "email": "sarah.c@cyberdyne.com", "tenure_days": 240, "total_spend": 2450.00, "recent_sentiment": "Positive", "open_tickets": 0, "churn_risk": 5.0, "status": "Active"},
            {"customer_id": "C-102", "name": "Bruce Wayne", "email": "bruce@waynecorp.com", "tenure_days": 45, "total_spend": 12500.00, "recent_sentiment": "Neutral", "open_tickets": 2, "churn_risk": 32.0, "status": "Active"},
            {"customer_id": "C-103", "name": "Peter Parker", "email": "peter@dailybugle.com", "tenure_days": 14, "total_spend": 49.00, "recent_sentiment": "Negative", "open_tickets": 3, "churn_risk": 84.0, "status": "At Risk"},
            {"customer_id": "C-104", "name": "Tony Stark", "email": "tony@starkindustries.com", "tenure_days": 365, "total_spend": 45000.00, "recent_sentiment": "Positive", "open_tickets": 0, "churn_risk": 2.0, "status": "Active"},
            {"customer_id": "C-105", "name": "Clark Kent", "email": "clark@dailyplanet.com", "tenure_days": 90, "total_spend": 149.00, "recent_sentiment": "Negative", "open_tickets": 1, "churn_risk": 54.0, "status": "At Risk"},
        ])
        # Calculate initial churn risks
        st.session_state.crm_data["churn_risk"] = st.session_state.crm_data.apply(predict_churn_risk, axis=1)

    if "tickets" not in st.session_state:
        st.session_state.tickets = [
            {"ticket_id": "T-1001", "customer_id": "C-102", "customer": "Bruce Wayne", "category": "Sales Inquiry", "issue": "Enterprise deployment invoice clearance query", "sentiment": "Neutral", "status": "Open", "created_at": "2026-07-18 10:24", "assignee": "Aria Stark"},
            {"ticket_id": "T-1002", "customer_id": "C-103", "customer": "Peter Parker", "category": "Technical Support", "issue": "Camera feed sync connection timeout - Error 408", "sentiment": "Negative", "status": "Open", "created_at": "2026-07-19 09:15", "assignee": "Miles Morales"},
            {"ticket_id": "T-1003", "customer_id": "C-105", "customer": "Clark Kent", "category": "Billing Issue", "issue": "Double charged for the Premium Plan in June", "sentiment": "Negative", "status": "Open", "created_at": "2026-07-19 14:02", "assignee": "Lois Lane"},
            {"ticket_id": "T-1004", "customer_id": "C-101", "customer": "Sarah Connor", "category": "General", "issue": "Requested backup recovery logs for compliance", "sentiment": "Positive", "status": "Closed", "created_at": "2026-07-15 11:00", "assignee": "John Connor"},
        ]

    if "handoff_queue" not in st.session_state:
        st.session_state.handoff_queue = {} # customer_id -> list of messages

    if "workflows" not in st.session_state:
        st.session_state.workflows = [
            {"id": "WF-1", "name": "Negative Sentiment Retention Escalation", "trigger": "Customer Sentiment is Negative", "action": "Trigger high-priority Support Ticket & notify #customer-success Slack channel", "active": True},
            {"id": "WF-2", "name": "High Value Churn Warning Alert", "trigger": "Customer Churn Risk > 70% and Spend > $1000", "action": "Email Customer Success Manager & create urgent CRM Follow-up deal", "active": True},
        ]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {
            "sales": [{"role": "assistant", "content": "Hello! I am your FlowPilot Sales assistant. I can guide you through our product plans, feature lists, pricing, or set up a product demo for your team. What would you like to explore?"}],
            "support": [{"role": "assistant", "content": "Hi there! I am your FlowPilot Technical Support bot. Let me know if you have password issues, bugs, error codes, or billing questions. I can help resolve them or create a formal ticket."}],
            "care": [{"role": "assistant", "content": "Greetings! I am the FlowPilot Customer Success companion. Ready to help review your usage metrics, help you upgrade plans, or look at how we can optimize your configuration."}]
        }

    if "kb_documents" not in st.session_state:
        st.session_state.kb_documents = [
            {"id": "DOC-1", "title": "FlowPilot Core Features & Pricing", "content": "FlowPilot AI features high-accuracy sentiment monitoring, voice synthesizers, CRM pipelines, and automatic workflow creations. Pricing plans are Starter ($49/mo), Growth ($149/mo), and Enterprise ($499/mo). Growth plan has unlimited CRM integrations and Slack webhooks.", "added_at": "2026-07-10"},
            {"id": "DOC-2", "title": "Password Reset Procedures", "content": "To reset passwords, users navigate to dashboard/login, click 'Forgot Password', and submit their email. An email token is sent valid for 24 hours. Clicking it prompts for a new alphanumeric password containing at least 8 characters.", "added_at": "2026-07-12"},
            {"id": "DOC-3", "title": "Webhook Integration details", "content": "Slack/Discord notifications can be triggered by calling POST to our integration endpoints. For Slack: POST to https://api.flowpilot.ai/integrations/slack with headers Content-Type: application/json and body containing {'text': message_body, 'channel': target_channel}.", "added_at": "2026-07-15"}
        ]
        
    if "integration_logs" not in st.session_state:
        st.session_state.integration_logs = []

    # Always initialize rag_chunks so chat page never crashes on first load.
    # RAG.py will repopulate this with full chunks when the user visits the KB page.
    if "rag_chunks" not in st.session_state:
        # Inline simple chunker (avoids circular import with RAG.py)
        def _simple_chunk(text, size=350):
            words = text.split()
            chunks, current = [], []
            for word in words:
                current.append(word)
                if sum(len(w) + 1 for w in current) >= size:
                    chunks.append(" ".join(current))
                    current = []
            if current:
                chunks.append(" ".join(current))
            return chunks

        initial_chunks = []
        for doc in st.session_state.kb_documents:
            for idx, chunk_text in enumerate(_simple_chunk(doc["content"])):
                initial_chunks.append({
                    "chunk_id": f"{doc['id']}-C{idx + 1}",
                    "title": doc["title"],
                    "content": chunk_text,
                    "added_at": doc["added_at"]
                })
        st.session_state.rag_chunks = initial_chunks


# --- Document Exporter (PDF) ---
class PDFReport(FPDF):
    def header(self):
        # Header title
        self.set_font('helvetica', 'B', 15)
        self.set_text_color(30, 41, 59)
        self.cell(0, 10, 'FLOWPILOT AI - TICKET & CRITICAL SYSTEMS REPORT', border=False, new_x="LMARGIN", new_y="NEXT", align='C')
        self.set_draw_color(99, 102, 241)
        self.set_line_width(0.8)
        self.line(10, 20, 200, 20)
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f'Page {self.page_no()} | Generated by FlowPilot System | Hackathon Prototype', align='C')

def create_pdf_report(ticket_data):
    """
    Generates a beautifully structured PDF document summarizing a ticket's information.
    """
    pdf = PDFReport()
    pdf.add_page()
    
    # Title Section
    pdf.set_font('helvetica', 'B', 16)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 10, f"Ticket Invoice ID: {ticket_data['ticket_id']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Info Grid
    pdf.set_font('helvetica', 'B', 11)
    pdf.set_text_color(30, 41, 59)
    
    # Row 1
    pdf.cell(50, 8, "Customer Name:")
    pdf.set_font('helvetica', '', 11)
    pdf.cell(50, 8, f"{ticket_data['customer']}")
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(40, 8, "Created At:")
    pdf.set_font('helvetica', '', 11)
    pdf.cell(50, 8, f"{ticket_data['created_at']}", new_x="LMARGIN", new_y="NEXT")
    
    # Row 2
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(50, 8, "Ticket Category:")
    pdf.set_font('helvetica', '', 11)
    pdf.cell(50, 8, f"{ticket_data['category']}")
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(40, 8, "Assignee Team:")
    pdf.set_font('helvetica', '', 11)
    pdf.cell(50, 8, f"{ticket_data['assignee']}", new_x="LMARGIN", new_y="NEXT")
    
    # Row 3
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(50, 8, "Sentiment Score:")
    pdf.set_font('helvetica', '', 11)
    pdf.cell(50, 8, f"{ticket_data['sentiment']}")
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(40, 8, "Current Status:")
    pdf.set_font('helvetica', '', 11)
    pdf.cell(50, 8, f"{ticket_data['status']}", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(10)
    
    # Detailed Issue Description Box
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 10, "Summary of Request / Complaint:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('helvetica', '', 11)
    pdf.set_text_color(51, 65, 85)
    pdf.set_fill_color(248, 250, 252)
    pdf.multi_cell(0, 8, f"\"{ticket_data['issue']}\"", border=1, align='L', fill=True)
    pdf.ln(10)
    
    # AI Sentiment recommendation
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 10, "AI Generated Operations Suggestion:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(71, 85, 105)
    s_label = ticket_data['sentiment']
    if s_label == "Negative":
        recommendation = "URGENT ACTION RECOMMENDED: Customer has demonstrated high frustration. Ticket has been auto-flagged in the CRM queue. Initiated retention discount protocols (20% monthly off offer) and scheduled live representative supervisor callback."
    else:
        recommendation = "Standard ticket queue handling. Monitor resolution within the 48-hour SLA period. Follow up with a satisfaction survey post-closure."
        
    pdf.multi_cell(0, 7, recommendation, border=1, align='L')
    
    # Signature Mock
    pdf.ln(25)
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(100, 6, "Approved Operations Lead:")
    pdf.cell(90, 6, "System Signature:")
    pdf.ln(6)
    pdf.set_font('helvetica', 'I', 10)
    pdf.cell(100, 6, "________________________")
    pdf.cell(90, 6, "FlowPilot AI Core Engine [VERIFIED]", new_x="LMARGIN", new_y="NEXT")
    
    # Return PDF bytes
    return pdf.output()
