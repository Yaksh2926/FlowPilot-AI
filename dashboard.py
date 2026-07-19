import streamlit as st
import pandas as pd
import altair as alt
from style import card

def render_dashboard_page():
    st.title("📊 Operational Analytics & Team Metrics")
    st.markdown("##### Executive overview of system sentiment, lifecycle performance, and human agent leaderboards.")

    df = st.session_state.crm_data
    tickets = st.session_state.tickets

    # --- KPI Indicators ---
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.metric("Total Account Value", f"${df['total_spend'].sum():,.2f}")
    with kpi_col2:
        st.metric("Avg Churn Risk", f"{df['churn_risk'].mean():.1f}%", delta="-2.4% (w/w)")
    with kpi_col3:
        st.metric("Support SLA Status", "98.2% Resolution", delta="+1.1% Target")
    with kpi_col4:
        st.metric("Overall CSAT Score", "4.85 / 5.0", delta="+0.05")

    st.markdown("---")

    # --- Charts Row ---
    chart_col1, chart_col2 = st.columns([1.2, 1])

    with chart_col1:
        st.markdown("#### Customer Churn Risk vs. Lifecycle Value (LTV)")
        
        # Scatter plot of risk vs value
        scatter_chart = alt.Chart(df).mark_circle(size=140, opacity=0.85).encode(
            x=alt.X('total_spend:Q', title='Account Total Spend ($)', axis=alt.Axis(format="$~s")),
            y=alt.Y('churn_risk:Q', title='Churn Risk (%)', scale=alt.Scale(domain=[0, 100])),
            color=alt.Color('recent_sentiment:N', title='Sentiment Indicator', scale=alt.Scale(
                domain=['Positive', 'Neutral', 'Negative'],
                range=['#10b981', '#f59e0b', '#ef4444']
            )),
            tooltip=[
                alt.Tooltip('name:N', title='Customer'),
                alt.Tooltip('total_spend:Q', title='LTV', format="$$,.2f"),
                alt.Tooltip('churn_risk:Q', title='Risk', format=".1f%"),
                alt.Tooltip('recent_sentiment:N', title='Sentiment')
            ]
        ).properties(
            height=300
        ).interactive()
        
        st.altair_chart(scatter_chart, use_container_width=True)

    with chart_col2:
        st.markdown("#### Customer Sentiment Breakdown")
        
        # Aggregate sentiment
        sent_counts = df['recent_sentiment'].value_counts().reset_index()
        sent_counts.columns = ['sentiment', 'count']
        
        bar_chart = alt.Chart(sent_counts).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
            x=alt.X('sentiment:N', title='Sentiment Profile', sort=['Positive', 'Neutral', 'Negative']),
            y=alt.Y('count:Q', title='Number of Accounts'),
            color=alt.Color('sentiment:N', scale=alt.Scale(
                domain=['Positive', 'Neutral', 'Negative'],
                range=['#10b981', '#f59e0b', '#ef4444']
            ), legend=None)
        ).properties(
            height=300
        )
        
        st.altair_chart(bar_chart, use_container_width=True)

    st.markdown("---")

    # --- Lower Row: Support Pipeline & Team Leaderboard ---
    bot_col1, bot_col2 = st.columns([1, 1])

    with bot_col1:
        st.markdown("#### Support Ticket Volumes & Status")
        
        # Count tickets status
        ticket_statuses = pd.DataFrame(tickets)
        if not ticket_statuses.empty:
            status_agg = ticket_statuses['status'].value_counts().reset_index()
            status_agg.columns = ['Status', 'Count']
            
            status_chart = alt.Chart(status_agg).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Status", type="nominal", scale=alt.Scale(
                    domain=['Open', 'Closed'],
                    range=['#6366f1', '#10b981']
                )),
                tooltip=['Status', 'Count']
            ).properties(height=240)
            
            st.altair_chart(status_chart, use_container_width=True)
        else:
            st.info("No tickets in the system.")

    with bot_col2:
        st.markdown("#### 🏆 Human Agent Leaderboard")
        
        # Leaderboard table
        leaderboard_data = pd.DataFrame([
            {"Agent": "Lois Lane", "Resolved": 48, "Avg Handle Time": "4.2m", "CSAT": "4.92 / 5.0", "Performance": "Excellent"},
            {"Agent": "Aria Stark", "Resolved": 35, "Avg Handle Time": "5.1m", "CSAT": "4.87 / 5.0", "Performance": "Outstanding"},
            {"Agent": "John Connor", "Resolved": 29, "Avg Handle Time": "6.0m", "CSAT": "4.81 / 5.0", "Performance": "High Tier"},
            {"Agent": "Miles Morales", "Resolved": 22, "Avg Handle Time": "5.5m", "CSAT": "4.75 / 5.0", "Performance": "Solid"},
        ])
        
        # Custom HTML styling for leaderboard
        leaderboard_html = """
        <div style="background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; overflow: hidden;">
            <table style="width: 100%; border-collapse: collapse; text-align: left; font-family: 'Outfit', sans-serif; font-size: 0.9rem; color: #f3f4f6;">
                <thead>
                    <tr style="background: rgba(15, 23, 42, 0.8); border-bottom: 2px solid rgba(255, 255, 255, 0.05);">
                        <th style="padding: 10px 15px; color: #38bdf8; font-weight: 600;">Agent Name</th>
                        <th style="padding: 10px 15px; color: #38bdf8; font-weight: 600; text-align: center;">Chats Resolved</th>
                        <th style="padding: 10px 15px; color: #38bdf8; font-weight: 600; text-align: center;">Handle Time</th>
                        <th style="padding: 10px 15px; color: #38bdf8; font-weight: 600; text-align: center;">CSAT</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for idx, row in leaderboard_data.iterrows():
            medal = "🥇 " if idx == 0 else ("🥈 " if idx == 1 else ("🥉 " if idx == 2 else "👤 "))
            leaderboard_html += f"""
                    <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); hover: background-color: rgba(99, 102, 241, 0.1);">
                        <td style="padding: 12px 15px; font-weight: 500;">{medal}{row['Agent']}</td>
                        <td style="padding: 12px 15px; text-align: center; font-weight: bold; color: #818cf8;">{row['Resolved']}</td>
                        <td style="padding: 12px 15px; text-align: center; color: #94a3b8;">{row['Avg Handle Time']}</td>
                        <td style="padding: 12px 15px; text-align: center; color: #10b981; font-weight: bold;">{row['CSAT']}</td>
                    </tr>
            """
            
        leaderboard_html += """
                </tbody>
            </table>
        </div>
        """
        
        st.markdown(leaderboard_html, unsafe_allow_html=True)

    st.markdown("---")

    # --- Bottom Row: Category Split + Conversation Volume ---
    trend_col1, trend_col2 = st.columns([1, 1])

    with trend_col1:
        st.markdown("#### 📂 Ticket Category Distribution")
        st.caption("Sales vs. Support vs. Customer Success vs. General split")

        t_df_cat = pd.DataFrame(tickets)
        if not t_df_cat.empty:
            # Normalize categories into 3 buckets
            def bucket_category(cat):
                cat_lower = cat.lower()
                if "sales" in cat_lower:
                    return "Sales"
                elif "support" in cat_lower or "tech" in cat_lower or "billing" in cat_lower:
                    return "Support"
                elif "care" in cat_lower or "retention" in cat_lower or "success" in cat_lower or "loyalty" in cat_lower:
                    return "Customer Success"
                else:
                    return "General"

            t_df_cat["bucket"] = t_df_cat["category"].apply(bucket_category)
            cat_agg = t_df_cat["bucket"].value_counts().reset_index()
            cat_agg.columns = ["Category", "Count"]

            cat_chart = alt.Chart(cat_agg).mark_bar(cornerRadiusTopRight=8, cornerRadiusBottomRight=8).encode(
                y=alt.Y("Category:N", title=None, sort="-x"),
                x=alt.X("Count:Q", title="Number of Tickets"),
                color=alt.Color("Category:N", scale=alt.Scale(
                    domain=["Sales", "Support", "Customer Success", "General"],
                    range=["#38bdf8", "#ef4444", "#10b981", "#f59e0b"]
                ), legend=None),
                tooltip=["Category", "Count"]
            ).properties(height=220)

            st.altair_chart(cat_chart, use_container_width=True)
        else:
            st.info("No ticket data available.")

    with trend_col2:
        st.markdown("#### 📈 Conversation Volume (Last 7 Days)")
        st.caption("Simulated daily interaction trend across all channels")

        # Simulated time-series data (replace with DB query in production)
        import datetime
        today = datetime.date.today()
        dates = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
        volume_data = pd.DataFrame({
            "Date": dates,
            "Sales": [12, 18, 14, 22, 19, 25, 28],
            "Support": [34, 28, 41, 36, 29, 38, 44],
            "Customer Success": [8, 11, 9, 14, 12, 16, 18],
        })
        volume_long = volume_data.melt("Date", var_name="Channel", value_name="Conversations")
        volume_long["Date"] = volume_long["Date"].astype(str)

        vol_chart = alt.Chart(volume_long).mark_line(point=True, strokeWidth=2.5).encode(
            x=alt.X("Date:O", title="Date"),
            y=alt.Y("Conversations:Q", title="Daily Conversations"),
            color=alt.Color("Channel:N", scale=alt.Scale(
                domain=["Sales", "Support", "Customer Success"],
                range=["#38bdf8", "#ef4444", "#10b981"]
            )),
            tooltip=["Date", "Channel", "Conversations"]
        ).properties(height=220).interactive()

        st.altair_chart(vol_chart, use_container_width=True)
