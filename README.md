# 🚀 FlowPilot AI

> **One AI Agent to Manage Sales, Support & Customer Success.**

FlowPilot AI is a unified intelligent agent platform that replaces three separate bots with one smart system — handling sales inquiries, technical support, and customer success in a single, beautiful interface.

---

## ✨ Features

### Phase 1 — Core MVP ✅
| Feature | Description |
|---|---|
| 🧠 Unified AI Agent | Single Claude-powered agent that detects intent and routes to Sales, Support, or CSM mode automatically |
| 💬 Chat Interface | 4-tab chat: Unified Agent + dedicated Sales, Support, and Care bots |
| 🗃️ CRM Records | Customer table with name, email, spend, tenure, open tickets, and lifecycle status |
| 🎫 Auto-Ticket Generation | Tickets created automatically on negative sentiment or explicit escalation keywords |
| 🛡️ Admin Dashboard | Manage tickets, live handoff queue, and webhook simulators |
| 📱 Conversation History | Full message history per customer context across sessions |

### Phase 2 — Differentiators ✅
| Feature | Description |
|---|---|
| 📚 RAG Knowledge Base | Upload `.txt`/`.md` docs; TF-IDF vector search grounds AI answers in your content |
| 🎭 Sentiment Analysis | Real-time sentiment tagging (Positive/Neutral/Negative) on every message |
| 📧 Email Generation | One-click AI-drafted follow-up email from any conversation |
| 📊 Analytics Dashboard | Churn vs LTV scatter, sentiment bars, ticket donut, category split, 7-day volume trend |
| 🏆 Team Leaderboard | Agent performance metrics (resolved, handle time, CSAT) |

### Phase 3 — Stretch ✅
| Feature | Description |
|---|---|
| 🎙️ Voice I/O | Web Speech API mic for voice input; text-to-speech for bot responses |
| 🤝 Live Human Handoff | Route any conversation to human agent queue in real-time |
| 🔍 Explainable AI | "Why did I answer this way?" panel for every bot response |
| 📉 Churn Prediction | Rule-based churn risk score (0–100%) per customer in CRM |
| ⚡ Workflow Builder | Natural language → automation rules with simulation sandbox |
| 🔗 Webhook Simulator | Slack, Discord, and WhatsApp notification payload simulator |

---

## 🛠️ Tech Stack

- **Frontend/Backend:** [Streamlit](https://streamlit.io/) (Python)  
- **AI:** [Anthropic Claude Sonnet 4.6](https://www.anthropic.com/) via `anthropic` SDK  
- **Charts:** [Altair](https://altair-viz.github.io/)  
- **Vector Search:** Custom TF-IDF cosine similarity engine (no external vector DB needed)  
- **PDF Export:** `fpdf2`  
- **Data:** `pandas` + `numpy` with in-memory session state  

---

## ⚡ Quick Start (Local)

### 1. Clone & Install

```bash
# Navigate to project directory
cd "Flowpilot AI"

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up API Key

```bash
# Option A: Set environment variable (recommended)
set ANTHROPIC_API_KEY=sk-ant-your-key-here    # Windows
export ANTHROPIC_API_KEY=sk-ant-your-key-here  # Mac/Linux

# Option B: Enter key in the app sidebar at runtime
# (The app works in simulation mode without a key for demo purposes)
```

### 3. Run the App

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Optional* | Anthropic Claude API key for live AI responses |

*Without a key, the app runs in **Simulation Mode** with a high-fidelity rule-based response engine — perfect for demos.

---

## 📁 Project Structure

```
Flowpilot AI/
├── app.py              # Entry point & navigation router
├── agent_prompt.py     # ⚙️ Central AI system prompts (tune here!)
├── chat.py             # Unified Agent + role-specific chat tabs
├── crm.py              # CRM portal & churn prediction
├── admin.py            # Admin console: tickets, handoffs, webhooks
├── dashboard.py        # Analytics charts & team metrics
├── RAG.py              # Knowledge base upload & retrieval engine
├── workflows.py        # Workflow builder & simulation sandbox
├── utils.py            # Claude AI client, sentiment, PDF export, mock data
├── style.py            # Glassmorphism CSS design system
├── requirements.txt    # Python dependencies
└── .env.example        # Environment variable template
```

---

## 🎯 Demo Flow (Hackathon Judges)

1. **Sidebar** → Enter your Anthropic Claude API key (or leave empty for simulation)
2. **🧠 Unified Agent** → Type "I want to cancel my subscription" → See intent detected + auto-ticket
3. **👥 CRM** → View churn risk scores, filter customers, add a new contact
4. **📚 RAG** → Upload a `.txt` FAQ → Ask a question → See grounded answer with citation
5. **📊 Analytics** → View sentiment trends, category split, conversation volume charts
6. **🛡️ Admin** → Manage the ticket pipeline, update SLA status, export PDF report
7. **⚡ Automations** → Create a natural language workflow → Run sandbox dry-run

---

## 🔒 Security Notes

- Never commit your `.env` file or API keys to version control
- The `ANTHROPIC_API_KEY` sidebar input is `type="password"` — not logged
- All data is stored in Streamlit session state (in-memory, resets on restart)

---

## 🏆 Built For

Open Innovation Hackathon — FlowPilot AI  
*Unified Operations Agent for Sales, Support & Customer Success*
