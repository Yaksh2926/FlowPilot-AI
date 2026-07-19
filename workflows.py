import streamlit as st
import time
import json
from style import card
from utils import generate_ai_response
from agent_prompt import WORKFLOW_PARSER_PROMPT

def parse_workflow_from_text(prompt):
    """
    Parses a workflow trigger and action from natural language input.
    Uses Gemini API if available, else rules-based parsing.
    """
    client = st.session_state.get("gemini_api_key", "")
    if client:
        try:
            res_text = generate_ai_response(prompt, system_instruction=WORKFLOW_PARSER_PROMPT)
            # Find JSON block
            import json
            import re
            json_match = re.search(r'\{.*\}', res_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return data.get("trigger", "Event occurred"), data.get("action", "Perform operation")
        except:
            pass
            
    # Heuristic parsing fallback
    p_lower = prompt.lower()
    trigger = "Customer event occurs"
    action = "Record log details"
    
    # Analyze triggers
    if "sentiment" in p_lower:
        trigger = "Sentiment drops to Negative"
    elif "churn" in p_lower or "risk" in p_lower:
        trigger = "Customer Churn Risk exceeds 60%"
    elif "ticket" in p_lower or "support" in p_lower:
        trigger = "New support ticket is created"
    elif "spend" in p_lower or "value" in p_lower:
        trigger = "Deal value exceeds $1,000"
    elif "upgrade" in p_lower:
        trigger = "Account upgrade request received"
        
    # Analyze actions
    if "slack" in p_lower or "notify channel" in p_lower:
        action = "Notify CS Team Slack Channel & create urgent CRM notification"
    elif "discord" in p_lower:
        action = "Post JSON payload block to Discord Developer Webhook"
    elif "email" in p_lower or "mail" in p_lower:
        action = "Draft automated customer retention email & send notification"
    elif "discount" in p_lower or "coupon" in p_lower:
        action = "Apply 15% discount coupon code automatically in Stripe"
    elif "ticket" in p_lower:
        action = "Generate support ticket and assign to high-tier staff"
    elif "assign" in p_lower:
        action = "Route chat account directly to senior representative"
        
    return trigger, action

def render_workflow_flowchart(trigger, action):
    """
    Generates a premium, glowing HTML/CSS node flowchart with smooth gradient lines.
    """
    flow_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem 0; width: 100%;">
        <!-- Node 1: Trigger -->
        <div style="
            background: rgba(99, 102, 241, 0.15);
            border: 2px solid #6366f1;
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            color: #f3f4f6;
            font-family: 'Outfit', sans-serif;
            text-align: center;
            max-width: 320px;
            z-index: 10;
        ">
            <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #818cf8; font-weight: bold; margin-bottom: 4px;">⚡ TRIGGER EVENT</div>
            <div style="font-size: 0.95rem; font-weight: 600;">{trigger}</div>
        </div>
        
        <!-- Connector Line 1 -->
        <div style="
            width: 3px;
            height: 40px;
            background: linear-gradient(to bottom, #6366f1, #38bdf8);
            box-shadow: 0 0 8px rgba(99, 102, 241, 0.4);
        "></div>
        
        <!-- Node 2: Evaluator -->
        <div style="
            background: rgba(30, 41, 59, 0.6);
            border: 1px dashed rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #38bdf8;
            font-size: 1.2rem;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            z-index: 10;
        ">
            ⚙️
        </div>
        
        <!-- Connector Line 2 -->
        <div style="
            width: 3px;
            height: 40px;
            background: linear-gradient(to bottom, #38bdf8, #10b981);
            box-shadow: 0 0 8px rgba(56, 189, 248, 0.4);
        "></div>
        
        <!-- Node 3: Action -->
        <div style="
            background: rgba(16, 185, 129, 0.15);
            border: 2px solid #10b981;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            color: #f3f4f6;
            font-family: 'Outfit', sans-serif;
            text-align: center;
            max-width: 320px;
            z-index: 10;
        ">
            <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #34d399; font-weight: bold; margin-bottom: 4px;">🚀 AUTOMATED ACTION</div>
            <div style="font-size: 0.95rem; font-weight: 600;">{action}</div>
        </div>
    </div>
    """
    st.components.v1.html(flow_html, height=300)

def render_workflows_page():
    st.title("⚡ Dynamic Workflow Automations")
    st.markdown("##### Describe operational processes in plain English to auto-create active workflows and trigger simulated logic loops.")
    
    col_w1, col_w2 = st.columns([1, 1])
    
    with col_w1:
        st.markdown("### ✍️ Generate New Agent Workflow")
        workflow_prompt = st.text_area(
            "Describe the automated workflow logic:",
            placeholder="E.g., If a customer requests cancellation, automatically apply a billing discount and notify Slack.",
            height=120
        )
        
        wf_name = st.text_input("Workflow Name", placeholder="E.g., Churn Prevention Slack Alert")
        
        if st.button("Auto-Create Workflow"):
            if workflow_prompt and wf_name:
                with st.spinner("Analyzing rules and generating trigger mappings..."):
                    trigger, action = parse_workflow_from_text(workflow_prompt)
                    
                # Save to st.session_state.workflows
                new_wf = {
                    "id": f"WF-{len(st.session_state.workflows)+1}",
                    "name": wf_name,
                    "trigger": trigger,
                    "action": action,
                    "active": True
                }
                st.session_state.workflows.append(new_wf)
                st.success(f"Created automation flow: **{wf_name}**!")
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Please fill out both the description and the workflow name.")
                
        # Display existing workflows list
        st.markdown("#### Active Automation Triggers")
        for wf in st.session_state.workflows:
            active_label = "✅ ACTIVE" if wf["active"] else "❌ INACTIVE"
            status_color = "green" if wf["active"] else "red"
            
            with st.expander(f"{wf['name']} ({active_label})"):
                st.write(f"**Trigger condition:** `{wf['trigger']}`")
                st.write(f"**Action script:** `{wf['action']}`")
                
                # Render mini flowchart in expander
                render_workflow_flowchart(wf["trigger"], wf["action"])

    with col_w2:
        st.markdown("### 🧪 Simulation Sandbox")
        st.info("Test how customer actions trigger your automation rules in real-time.")
        
        # Test inputs
        sim_sentiment = st.selectbox("Simulate Customer Sentiment", ["Positive", "Neutral", "Negative"])
        sim_churn = st.slider("Simulate Customer Churn Risk %", 0, 100, 45)
        sim_spend = st.number_input("Simulate Customer Spend ($)", min_value=0.0, value=250.0)
        
        if st.button("Run Automation Dry Run"):
            st.write("---")
            st.write("**Evaluating rules against simulated metrics:**")
            
            triggered_any = False
            
            # Check Workflow 1
            if sim_sentiment == "Negative":
                st.success("🔥 **Trigger Match!** Triggered workflow: *Negative Sentiment Retention Escalation*")
                st.write("- **Executed Action**: Notify CS Team Slack Channel & create urgent CRM notification")
                
                # Log log message
                st.session_state.integration_logs.append({
                    "time": time.strftime("%H:%M:%S"),
                    "webhook": "Slack Integration Service",
                    "payload": {
                        "text": "[ALERT] Customer submitted negative feedback. High priority review initiated.",
                        "channel": "#customer-success",
                        "severity": "CRITICAL"
                    }
                })
                triggered_any = True
                
            # Check Workflow 2
            if sim_churn > 70 and sim_spend > 1000:
                st.success("🔥 **Trigger Match!** Triggered workflow: *High Value Churn Warning Alert*")
                st.write("- **Executed Action**: Email Customer Success Manager & create urgent CRM Follow-up deal")
                
                st.session_state.integration_logs.append({
                    "time": time.strftime("%H:%M:%S"),
                    "webhook": "Email Integration Service",
                    "payload": {
                        "to": "csm_lead@flowpilot.ai",
                        "subject": "Warning: High Churn risk alert (Value: $" + str(sim_spend) + ")",
                        "customer": "Simulated High-Value Contact"
                    }
                })
                triggered_any = True
                
            # Custom workflows check
            for wf in st.session_state.workflows:
                if wf["id"] in ["WF-1", "WF-2"]:
                    continue
                # Heuristic eval of trigger matching
                trig_l = wf["trigger"].lower()
                matched = False
                if "sentiment" in trig_l and sim_sentiment == "Negative":
                    matched = True
                elif "churn" in trig_l and sim_churn > 60:
                    matched = True
                elif "spend" in trig_l and sim_spend > 1000:
                    matched = True
                    
                if matched:
                    st.success(f"🔥 **Trigger Match!** Triggered Custom workflow: *{wf['name']}*")
                    st.write(f"- **Executed Action**: {wf['action']}")
                    st.session_state.integration_logs.append({
                        "time": time.strftime("%H:%M:%S"),
                        "webhook": "Custom Automation Runner",
                        "payload": {
                            "workflow_id": wf["id"],
                            "trigger_matched": wf["trigger"],
                            "action_taken": wf["action"]
                        }
                    })
                    triggered_any = True
                    
            if not triggered_any:
                st.info("Metrics do not match any active automation triggers. Sandbox state is nominal.")
                
        # Integration Logs
        st.markdown("#### Live Execution Webhook Logs (Slack / Email / Web)")
        if st.session_state.integration_logs:
            for log in reversed(st.session_state.integration_logs[-4:]):
                st.markdown(f"""
                <div style="background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 6px; padding: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="color: #94a3b8; font-size: 0.8rem;">[{log['time']}]</span> 
                    <span style="color: #38bdf8; font-weight: bold; font-size: 0.8rem;">{log['webhook']}</span>
                    <pre style="margin: 4px 0 0 0; font-size: 0.75rem; color: #a5b4fc; background: none; border: none; padding: 0;">{json.dumps(log['payload'], indent=2)}</pre>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("No logs recorded yet. Run dry-runs to see payloads.")
