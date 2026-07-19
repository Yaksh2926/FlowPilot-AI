import streamlit as st
import pandas as pd
from style import card
from utils import predict_churn_risk

def render_crm_page():
    st.title("👥 CRM Portal & Churn Prediction")
    st.markdown("##### Manage customer lifecycle data, inspect customer history, and predict churn risk.")

    # Access shared session data
    df = st.session_state.crm_data

    # Display Metrics Header
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Contacts", len(df))
    with col2:
        active_count = len(df[df["status"] == "Active"])
        st.metric("Active Accounts", active_count)
    with col3:
        at_risk_count = len(df[df["status"] == "At Risk"])
        st.metric("At Risk Accounts", at_risk_count, delta=f"{at_risk_count} Alert", delta_color="inverse")
    with col4:
        total_val = f"${df['total_spend'].sum():,.2f}"
        st.metric("Total Account Value", total_val)

    st.markdown("---")

    # Layout for Search and Add
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.markdown("### Customer Directory")
        search_query = st.text_input("🔍 Search Customers by Name or Email", "")
        
        # Filter data
        if search_query:
            filtered_df = df[
                df["name"].str.contains(search_query, case=False) | 
                df["email"].str.contains(search_query, case=False)
            ]
        else:
            filtered_df = df

        # Add visual highlighting for Churn Risk
        def highlight_churn(val):
            if val > 60:
                return 'background-color: rgba(239, 68, 68, 0.15); color: #ef4444; font-weight: bold;'
            elif val > 30:
                return 'background-color: rgba(245, 158, 11, 0.15); color: #f59e0b;'
            else:
                return 'background-color: rgba(16, 185, 129, 0.15); color: #10b981;'

        # Styled Table Display
        styled_df = filtered_df.style.map(highlight_churn, subset=["churn_risk"])
        st.dataframe(
            styled_df, 
            use_container_width=True, 
            column_config={
                "customer_id": "ID",
                "name": "Full Name",
                "email": "Email",
                "tenure_days": "Tenure (Days)",
                "total_spend": st.column_config.NumberColumn("Total Spend ($)", format="$%.2f"),
                "recent_sentiment": "Recent Sentiment",
                "open_tickets": "Open Tickets",
                "churn_risk": st.column_config.ProgressColumn("Churn Risk %", format="%.1f%%", min_value=0, max_value=100),
                "status": "Lifecycle Status"
            },
            hide_index=True
        )

    with right_col:
        st.markdown("### ➕ Register New Customer")
        with st.form("add_customer_form", clear_on_submit=True):
            new_id = f"C-{100 + len(df) + 1}"
            new_name = st.text_input("Name", placeholder="Tony Stark")
            new_email = st.text_input("Email", placeholder="tony@stark.com")
            new_tenure = st.number_input("Tenure (Days)", min_value=0, value=30)
            new_spend = st.number_input("Total Spend ($)", min_value=0.0, value=200.0, step=50.0)
            new_sentiment = st.selectbox("Recent Sentiment", ["Positive", "Neutral", "Negative"])
            new_status = st.selectbox("Status", ["Active", "At Risk"])
            
            submit_btn = st.form_submit_button("Add Customer Record")
            
            if submit_btn:
                if new_name and new_email:
                    new_row = {
                        "customer_id": new_id,
                        "name": new_name,
                        "email": new_email,
                        "tenure_days": int(new_tenure),
                        "total_spend": float(new_spend),
                        "recent_sentiment": new_sentiment,
                        "open_tickets": 0,
                        "status": new_status
                    }
                    # Calculate churn risk using logic
                    new_row["churn_risk"] = predict_churn_risk(new_row)
                    
                    # Update global session state DataFrame
                    st.session_state.crm_data = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"Successfully registered {new_name} (ID: {new_id})!")
                    st.rerun()
                else:
                    st.error("Please fill out the Name and Email fields.")

    st.markdown("---")

    # CRM Insights & Details Explorer
    st.markdown("### 🔍 Customer Timeline & Deep-Dive Analytics")
    selected_customer_name = st.selectbox("Select Customer to Profile", df["name"].tolist())
    
    if selected_customer_name:
        cust_record = df[df["name"] == selected_customer_name].iloc[0]
        c_id = cust_record["customer_id"]
        
        col_c1, col_c2 = st.columns([1, 1])
        
        with col_c1:
            # Render customer details
            risk = cust_record['churn_risk']
            if risk > 60:
                risk_badge = f'<span class="status-pill status-negative">High Risk ({risk:.1f}%)</span>'
            elif risk > 30:
                risk_badge = f'<span class="status-pill status-neutral">Medium Risk ({risk:.1f}%)</span>'
            else:
                risk_badge = f'<span class="status-pill status-positive">Low Risk ({risk:.1f}%)</span>'
                
            sentiment_badge = f'<span class="status-pill status-{cust_record["recent_sentiment"].lower()}">{cust_record["recent_sentiment"]}</span>'

            card(
                f"Customer Dossier: {cust_record['name']} ({c_id})",
                f"""
                <table style="width:100%; border-collapse: collapse; color:#f3f4f6;">
                    <tr><td style="padding: 6px 0; font-weight:bold; width:45%;">Email Address:</td><td>{cust_record['email']}</td></tr>
                    <tr><td style="padding: 6px 0; font-weight:bold;">Customer Tenure:</td><td>{cust_record['tenure_days']} Days</td></tr>
                    <tr><td style="padding: 6px 0; font-weight:bold;">Total Life-Time Value:</td><td>${cust_record['total_spend']:,.2f}</td></tr>
                    <tr><td style="padding: 6px 0; font-weight:bold;">Active Tickets:</td><td>{cust_record['open_tickets']} Open</td></tr>
                    <tr><td style="padding: 6px 0; font-weight:bold;">Sentiment Score:</td><td>{sentiment_badge}</td></tr>
                    <tr><td style="padding: 6px 0; font-weight:bold;">ML Churn Warning:</td><td>{risk_badge}</td></tr>
                    <tr><td style="padding: 6px 0; font-weight:bold;">Account Health:</td><td>{cust_record['status']}</td></tr>
                </table>
                """
            )
            
        with col_c2:
            st.markdown("#### Explainable AI Model Interpretation")
            st.info("The AI computes churn risk using historical support engagement and sentiment weights.")
            
            # Show feature contributions visually
            st.write("**Feature Importance Contributions:**")
            
            # Simple bar visualization using native streamlit
            c_tickets = cust_record["open_tickets"]
            c_sentiment = cust_record["recent_sentiment"]
            c_tenure = cust_record["tenure_days"]
            
            feat_contribs = {
                "Open Tickets Escalation": min(c_tickets * 15, 60),
                "Customer Sentiment Modifier": 35 if c_sentiment == "Negative" else (-10 if c_sentiment == "Positive" else 0),
                "Account Lifecycle Tenure": 12 if c_tenure < 30 else (-10 if c_tenure > 180 else 0)
            }
            
            for key, val in feat_contribs.items():
                direction = "📈 Increase Risk" if val > 0 else ("📉 Decrease Risk" if val < 0 else "➖ Neutral")
                st.write(f"- **{key}**: `{val:+.1f}%` ({direction})")
                
            st.caption("AI Model Decision Path: Risk = Base (15%) + Tickets (+15%/ea) + Sentiment (+35%/-10%) + Tenure (+12%/-10%)")
