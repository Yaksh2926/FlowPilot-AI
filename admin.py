import streamlit as st
import pandas as pd
import time
from style import card
from utils import create_pdf_report

def render_admin_page():
    st.title("🛡️ Admin Console & Operations Center")
    st.markdown("##### Manage live human agent handoffs, inspect active ticket SLA statuses, and simulate enterprise webhooks.")

    # Access state
    tickets = st.session_state.tickets
    handoffs = st.session_state.handoff_queue
    df_crm = st.session_state.crm_data

    # Layout Tabs
    tab_handoff, tab_tickets, tab_integrations = st.tabs([
        "💬 Live Human Handoff Queue", 
        "🎫 Support Tickets Pipeline", 
        "🔗 Channel Webhook Simulator"
    ])

    # --- TAB 1: Live Handoff Queue ---
    with tab_handoff:
        st.markdown("### Active Handoff Inbox")
        
        # Filter active handoffs (where queue contains chats)
        active_handoff_keys = [k for k, v in handoffs.items() if len(v) > 0]
        
        if not active_handoff_keys:
            st.info("Excellent! The human agent handoff queue is currently empty. All queries resolved by automated agents.")
        else:
            col_queue, col_chat = st.columns([1, 2])
            
            with col_queue:
                st.markdown("**Awaiting Agent response:**")
                selected_c_id = st.selectbox(
                    "Select Customer Conversation",
                    active_handoff_keys,
                    format_func=lambda x: f"{df_crm[df_crm['customer_id'] == x]['name'].values[0]} ({x})"
                )
            
            with col_chat:
                if selected_c_id:
                    cust_name = df_crm[df_crm['customer_id'] == selected_c_id]['name'].values[0]
                    st.markdown(f"#### Chat Session: {cust_name}")
                    
                    # Display transcript
                    chat_window = st.container(height=300)
                    for msg in handoffs[selected_c_id]:
                        role_label = "👤 Customer" if msg["role"] == "user" else "🛡️ Agent (You)"
                        align = "left" if msg["role"] == "user" else "right"
                        bg = "rgba(255, 255, 255, 0.05)" if msg["role"] == "user" else "rgba(99, 102, 241, 0.15)"
                        
                        chat_window.markdown(f"""
                        <div style="background: {bg}; border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem; text-align: {align};">
                            <strong style="color: #38bdf8; font-size: 0.8rem;">{role_label}</strong><br>
                            <span style="font-size: 0.95rem;">{msg['content']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    # Send response
                    with st.form("human_response_form", clear_on_submit=True):
                        human_msg = st.text_input("Type response as Human Support Agent...", key="human_reply")
                        col_btn1, col_btn2 = st.columns([1, 1])
                        
                        with col_btn1:
                            submit_reply = st.form_submit_button("Send Reply")
                        with col_btn2:
                            resolve_chat = st.form_submit_button("✅ Resolve & Close Session")
                            
                        if submit_reply and human_msg:
                            # Append to queue
                            st.session_state.handoff_queue[selected_c_id].append({
                                "role": "assistant",
                                "content": human_msg
                            })
                            # Append also to support chat history
                            st.session_state.chat_history["support"].append({
                                "role": "assistant",
                                "content": f"[Live Agent Response]: {human_msg}"
                            })
                            st.success("Message transmitted!")
                            time.sleep(0.5)
                            st.rerun()
                            
                        if resolve_chat:
                            # Clear the queue for this customer
                            st.session_state.handoff_queue[selected_c_id] = []
                            st.success("Handoff session resolved. Returning control to automated agent.")
                            
                            # Increment customer resolved metric (simulated)
                            st.session_state.crm_data.loc[
                                st.session_state.crm_data["customer_id"] == selected_c_id, 
                                "open_tickets"
                            ] = max(0, int(df_crm[df_crm['customer_id'] == selected_c_id]['open_tickets'].values[0] - 1))
                            
                            time.sleep(0.5)
                            st.rerun()

    # --- TAB 2: Ticket Pipeline ---
    with tab_tickets:
        st.markdown("### System Generated Tickets")
        
        # Display as a table with controls
        t_df = pd.DataFrame(tickets)
        
        if not t_df.empty:
            # Columns selector
            selected_ticket_id = st.selectbox("Select Ticket to Inspect / Export", t_df["ticket_id"].tolist())
            
            # Show ticket options
            t_record = next(item for item in tickets if item["ticket_id"] == selected_ticket_id)
            
            st.markdown(f"#### Ticket: {t_record['ticket_id']} ({t_record['category']})")
            
            col_t1, col_t2 = st.columns([2, 1])
            with col_t1:
                card(
                    f"Issue Details - Owner: {t_record['customer']}",
                    f"""
                    <strong>Created At:</strong> {t_record['created_at']}<br>
                    <strong>Assigned Resolver:</strong> {t_record['assignee']}<br>
                    <strong>Customer sentiment:</strong> <span class="status-pill status-{t_record['sentiment'].lower()}">{t_record['sentiment']}</span><br>
                    <strong>Ticket status:</strong> {t_record['status']}<br>
                    <p style="margin-top: 10px; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px; border-left: 2px solid #818cf8; font-style: italic;">
                        "{t_record['issue']}"
                    </p>
                    """
                )
            
            with col_t2:
                # Update status
                st.write("**Manage Ticket Actions**")
                new_status = st.selectbox("Update SLA Status", ["Open", "Closed"], index=0 if t_record["status"] == "Open" else 1)
                if st.button("Apply Status Change"):
                    t_record["status"] = new_status
                    # Update open tickets count in CRM data
                    c_id = t_record["customer_id"]
                    t_count = len([t for t in tickets if t["customer_id"] == c_id and t["status"] == "Open"])
                    st.session_state.crm_data.loc[st.session_state.crm_data["customer_id"] == c_id, "open_tickets"] = t_count
                    st.success("Ticket status updated in CRM database!")
                    time.sleep(0.5)
                    st.rerun()
                
                # Export PDF
                try:
                    pdf_bytes = create_pdf_report(t_record)
                    st.download_button(
                        label="📄 Export Ticket Report (PDF)",
                        data=pdf_bytes,
                        file_name=f"FlowPilot_Report_{t_record['ticket_id']}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Could not generate PDF: {e}")
                    
            st.markdown("---")
            st.markdown("#### Full Tickets Log Table")
            st.dataframe(t_df, use_container_width=True, hide_index=True)
        else:
            st.info("No tickets present in database logs.")

    # --- TAB 3: Channels Integration Simulator ---
    with tab_integrations:
        st.markdown("### Corporate Integration Gateways")
        st.markdown("Simulate triggering live webhook triggers to Slack, Discord, or customer WhatsApp channels.")
        
        col_i1, col_i2, col_i3 = st.columns(3)
        
        with col_i1:
            card(
                "Slack Integration",
                """
                <strong>Status:</strong> <span style="color: #10b981; font-weight: bold;">CONNECTED</span><br>
                <strong>Route:</strong> <code>#customer-alerts</code><br>
                Trigger live chat-sentiment notification payloads to Slack workspaces.
                """
            )
            slack_test_msg = st.text_input("Slack Message Test", "Urgent escalation needed for Sarah Connor.", key="slack_test")
            if st.button("Trigger Slack Webhook Payload"):
                # Append to logs
                st.session_state.integration_logs.append({
                    "time": time.strftime("%H:%M:%S"),
                    "webhook": "Slack Webhook Router",
                    "payload": {
                        "webhook_url": "https://hooks.slack.com/services/T00/B00/FP_ALERT",
                        "channel": "#customer-alerts",
                        "username": "FlowPilot AI Bot",
                        "attachments": [{
                            "color": "#ef4444",
                            "text": slack_test_msg,
                            "timestamp": int(time.time())
                        }]
                    }
                })
                st.success("Slack simulated webhook payload dispatched! Check logs in Workflows tab.")
                
        with col_i2:
            card(
                "Discord Integration",
                """
                <strong>Status:</strong> <span style="color: #10b981; font-weight: bold;">CONNECTED</span><br>
                <strong>Route:</strong> <code>#crm-feed</code><br>
                Broadcast live lead values and CRM deal expansions to developer discord.
                """
            )
            discord_test_msg = st.text_input("Discord Embed Details", "New Opportunity Registered: Stark Labs ($45k)", key="discord_test")
            if st.button("Trigger Discord Alert"):
                st.session_state.integration_logs.append({
                    "time": time.strftime("%H:%M:%S"),
                    "webhook": "Discord Endpoint Hub",
                    "payload": {
                        "url": "https://discord.com/api/webhooks/999/flowpilot",
                        "content": "🚀 CRM Event Triggered",
                        "embeds": [{
                            "title": "Deal Flow Expansion Alert",
                            "description": discord_test_msg,
                            "color": 65280
                        }]
                    }
                })
                st.success("Discord embed notification payload successfully simulated!")
                
        with col_i3:
            card(
                "WhatsApp API Simulation",
                """
                <strong>Status:</strong> <span style="color: #f59e0b; font-weight: bold;">SANDBOX</span><br>
                <strong>Phone:</strong> <code>+1 (555) 019-9022</code><br>
                Deliver direct notification SMS and support transcripts via WhatsApp channels.
                """
            )
            wa_msg = st.text_input("WhatsApp Push Content", "Hi Bruce, your support ticket T-1001 is now solved.", key="wa_test")
            if st.button("Push WhatsApp Message"):
                st.session_state.integration_logs.append({
                    "time": time.strftime("%H:%M:%S"),
                    "webhook": "WhatsApp Cloud API",
                    "payload": {
                        "messaging_product": "whatsapp",
                        "to": "+15550199022",
                        "type": "template",
                        "template": {
                            "name": "ticket_update_notification",
                            "language": {
                                "code": "en_US"
                            },
                            "components": [{
                                "type": "body",
                                "parameters": [{"type": "text", "text": wa_msg}]
                            }]
                        }
                    }
                })
                st.success("WhatsApp template packet parsed & sent to sandbox queue!")
