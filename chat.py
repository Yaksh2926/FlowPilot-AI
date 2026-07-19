import streamlit as st
import time
import re
from style import card
from utils import (
    generate_ai_response, 
    analyze_sentiment, 
    get_explainable_ai_reason,
    predict_churn_risk
)
from agent_prompt import (
    UNIFIED_AGENT_PROMPT,
    SALES_AGENT_PROMPT,
    SUPPORT_AGENT_PROMPT,
    CARE_AGENT_PROMPT,
    RAG_SYSTEM_PROMPT,
    EMAIL_DRAFT_PROMPT,
    EXPLAINABLE_AI_PROMPT
)

# --- Voice to Streamlit integration via Iframe URL redirect ---
def render_voice_rec_widget():
    """
    Renders a premium visual glowing mic button that transcribes browser speech
    and reloads Streamlit with the transcribed query parameter.
    """
    mic_html = """
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 10px; font-family: 'Outfit', sans-serif;">
        <button id="mic-btn" style="
            background: radial-gradient(circle, #ff4b4b 0%, #d62222 100%);
            border: none;
            border-radius: 50%;
            width: 55px;
            height: 55px;
            cursor: pointer;
            box-shadow: 0 0 15px rgba(255, 75, 75, 0.6);
            color: white;
            font-size: 1.5rem;
            transition: all 0.3s ease;
            outline: none;
        ">
            🎙️
        </button>
        <span id="speech-status" style="margin-top: 8px; font-size: 0.8rem; color: #94a3b8;">Click mic to speak</span>
        
        <script>
            const btn = document.getElementById('mic-btn');
            const status = document.getElementById('speech-status');
            
            btn.onclick = function() {
                window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!window.SpeechRecognition) {
                    status.innerHTML = "❌ Browser Speech Not Supported";
                    return;
                }
                
                const recognition = new window.SpeechRecognition();
                recognition.interimResults = false;
                recognition.lang = 'en-US';
                
                status.innerHTML = "🔊 Listening...";
                btn.style.boxShadow = "0 0 25px rgba(255, 75, 75, 1)";
                btn.style.transform = "scale(1.08)";
                
                recognition.start();
                
                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript;
                    status.innerHTML = "✅ Transcribed!";
                    btn.style.transform = "scale(1)";
                    btn.style.boxShadow = "0 0 15px rgba(16, 185, 129, 0.6)";
                    btn.style.background = "linear-gradient(135deg, #10b981 0%, #059669 100%)";
                    
                    // Redirect back to parent Streamlit URL with query parameters
                    setTimeout(() => {
                        const url = new URL(window.parent.location.href);
                        url.searchParams.set("voice_input", transcript);
                        window.parent.location.href = url.toString();
                    }, 500);
                };
                
                recognition.onerror = function(event) {
                    status.innerHTML = "❌ Error: " + event.error;
                    btn.style.boxShadow = "0 0 15px rgba(255, 75, 75, 0.6)";
                    btn.style.transform = "scale(1)";
                };
                
                recognition.onspeechend = function() {
                    recognition.stop();
                };
            };
        </script>
    </div>
    """
    st.components.v1.html(mic_html, height=120)

def render_voice_speak_widget(text):
    """
    Injects a Javascript speech synthesis trigger to speak the text out loud.
    """
    clean_text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', text)
    speak_html = f"""
    <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel(); // Stop any current speech
            const utterance = new SpeechSynthesisUtterance("{clean_text}");
            utterance.rate = 1.05;
            utterance.pitch = 1.0;
            // Get available voices
            const voices = window.speechSynthesis.getVoices();
            // Optional filter for premium voices
            if (voices.length > 0) {{
                utterance.voice = voices[0];
            }}
            window.speechSynthesis.speak(utterance);
        }}
    </script>
    """
    st.components.v1.html(speak_html, height=0)

def render_chat_page():
    st.title("🤖 Customer Support Center")
    st.markdown("##### Interact with FlowPilot Bots or toggle Voice, Sentiment analysis, and human handoff protocols.")

    # Detect voice query params from our Speech API iframe
    # Streamlit >= 1.30 query params reading:
    voice_query_val = ""
    if hasattr(st, "query_params") and "voice_input" in st.query_params:
        voice_query_val = st.query_params["voice_input"]
        # Clear it from url to prevent repeat trigger
        st.query_params.clear()

    # User Configuration state
    df_crm = st.session_state.crm_data

    # Selector for active customer context
    c_list = df_crm["name"].tolist()
    
    col_sel1, col_sel2 = st.columns([1, 1])
    with col_sel1:
        active_c_name = st.selectbox("Simulate Customer Context", c_list)
        cust_record = df_crm[df_crm["name"] == active_c_name].iloc[0]
        c_id = cust_record["customer_id"]
    with col_sel2:
        voice_enabled = st.checkbox("🔊 Voice Speech Feedback (Speak bot responses aloud)", value=False)

    st.markdown("---")

    # Bot Role Tab Selector — Unified agent first, then individual role tabs
    bot_tab_unified, bot_tab_sales, bot_tab_support, bot_tab_care = st.tabs([
        "🧠 Unified Agent",
        "💰 Sales Assistant Bot",
        "🛠️ Tech Support Bot",
        "🎯 Customer Care & Loyalty Bot"
    ])

    # ── UNIFIED AGENT TAB ──────────────────────────────────────────────────────
    with bot_tab_unified:
        st.write("**FlowPilot Unified Agent** — detects your intent and responds as Sales, Support, or Customer Success automatically.")
        st.caption("One agent to handle everything. Just type your message.")

        is_handed_off = c_id in st.session_state.handoff_queue and len(st.session_state.handoff_queue[c_id]) > 0
        if is_handed_off:
            st.warning(f"⚠️ Live Human Agent Handoff active for {active_c_name}. Bot operations suspended.")

        hist_key = "chat_unified"
        if hist_key not in st.session_state:
            st.session_state[hist_key] = [
                {"role": "assistant", "content": "Hello! I'm FlowPilot's Unified AI Agent. I handle Sales, Support, and Customer Success — just tell me what you need and I'll route your request automatically. 🚀"}
            ]

        unified_container = st.container(height=380)
        for msg in st.session_state[hist_key]:
            with unified_container.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg["role"] == "user":
                    sent, score, col_cls = analyze_sentiment(msg["content"])
                    st.markdown(f'<span class="status-pill {col_cls}">Sentiment: {sent} ({int(score*100)}%)</span>', unsafe_allow_html=True)

        unified_prompt = st.chat_input("Ask anything — sales, support, or account help...", key="input_unified")
        if unified_prompt and not is_handed_off:
            st.session_state[hist_key].append({"role": "user", "content": unified_prompt})
            with unified_container.chat_message("user"):
                st.write(unified_prompt)
                sent, score, col_cls = analyze_sentiment(unified_prompt)
                st.markdown(f'<span class="status-pill {col_cls}">Sentiment: {sent} ({int(score*100)}%)</span>', unsafe_allow_html=True)
                st.session_state.crm_data.loc[st.session_state.crm_data["customer_id"] == c_id, "recent_sentiment"] = sent
                new_risk = predict_churn_risk(st.session_state.crm_data[st.session_state.crm_data["customer_id"] == c_id].iloc[0])
                st.session_state.crm_data.loc[st.session_state.crm_data["customer_id"] == c_id, "churn_risk"] = new_risk

            with unified_container.chat_message("assistant"):
                with st.spinner("Unified Agent is routing and synthesizing response..."):
                    # Build RAG context if available (only after RAG page has been visited)
                    context = ""
                    if "rag_chunks" in st.session_state:
                        from RAG import compute_tfidf, retrieve_top_chunks
                        chunks = st.session_state.rag_chunks
                        if chunks:
                            tfidf_docs = [{"id": c["chunk_id"], "content": c["content"]} for c in chunks]
                            doc_vectors, idf = compute_tfidf(tfidf_docs)
                            results = retrieve_top_chunks(unified_prompt, chunks, doc_vectors, idf, top_n=1)
                            if results:
                                context = f"\n[RAG Context from '{results[0][1]['title']}': {results[0][1]['content']}]"

                    full_system = UNIFIED_AGENT_PROMPT + f"\nCustomer context: Name={active_c_name}, Spend=${cust_record['total_spend']:,.0f}, Open Tickets={cust_record['open_tickets']}, Sentiment={cust_record['recent_sentiment']}" + context
                    answer = generate_ai_response(unified_prompt, system_instruction=full_system)
                    st.write(answer)

                    if voice_enabled:
                        render_voice_speak_widget(answer)

            st.session_state[hist_key].append({"role": "assistant", "content": answer})

            # Auto-ticket from unified agent marker
            if "AUTO-TICKET:" in answer:
                ticket_title = answer.split("AUTO-TICKET:")[-1].strip().split("\n")[0][:80]
                ticket_id = f"T-{1000 + len(st.session_state.tickets) + 1}"
                new_ticket = {
                    "ticket_id": ticket_id,
                    "customer_id": c_id,
                    "customer": active_c_name,
                    "category": "Unified Agent Auto-Escalation",
                    "issue": ticket_title,
                    "sentiment": sent,
                    "status": "Open",
                    "created_at": time.strftime("%Y-%m-%d %H:%M"),
                    "assignee": "Aria Stark"
                }
                st.session_state.tickets.append(new_ticket)
                st.session_state.crm_data.loc[st.session_state.crm_data["customer_id"] == c_id, "open_tickets"] += 1
                st.warning(f"⚡ Auto-ticket **{ticket_id}** created: _{ticket_title}_")
            elif "negative" in sent.lower():
                ticket_id = f"T-{1000 + len(st.session_state.tickets) + 1}"
                new_ticket = {
                    "ticket_id": ticket_id,
                    "customer_id": c_id,
                    "customer": active_c_name,
                    "category": "Unified Agent — Sentiment Escalation",
                    "issue": f"Negative sentiment detected: \"{unified_prompt[:80]}\"",
                    "sentiment": sent,
                    "status": "Open",
                    "created_at": time.strftime("%Y-%m-%d %H:%M"),
                    "assignee": "Aria Stark"
                }
                st.session_state.tickets.append(new_ticket)
                st.session_state.crm_data.loc[st.session_state.crm_data["customer_id"] == c_id, "open_tickets"] += 1
                st.warning(f"⚡ Workflow Trigger: Ticket **{ticket_id}** auto-generated due to Negative Sentiment!")

            st.rerun()

        # Unified agent actions
        st.markdown("---")
        ua_col1, ua_col2, ua_col3 = st.columns([1, 1.2, 1])
        with ua_col1:
            st.write("**Voice Input**")
            render_voice_rec_widget()
        with ua_col2:
            st.write("**Live Escalation**")
            if st.button("🚨 Hand off to Human Agent", key="ho_unified"):
                st.session_state.handoff_queue[c_id] = [
                    {"role": "user", "content": f"[SYSTEM]: Human handoff requested. Last message: \"{st.session_state[hist_key][-1]['content'] if len(st.session_state[hist_key]) > 1 else 'None'}\""}
                ]
                st.success("Routed to Live Agent desk!")
                time.sleep(1)
                st.rerun()
        with ua_col3:
            st.write("**Follow-up Email**")
            if st.button("📧 Draft Follow-up Email", key="em_unified"):
                dialogue_str = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state[hist_key][-3:]])
                email_prompt = f"Conversation:\n{dialogue_str}\n\nDraft Email:"
                with st.spinner("Drafting email..."):
                    email_draft = generate_ai_response(email_prompt, system_instruction=EMAIL_DRAFT_PROMPT)
                st.markdown("#### 📧 Email Draft:")
                st.text_area("Edit before sending", value=email_draft, height=200, key="email_unified")

    # ── ROLE-SPECIFIC TABS ─────────────────────────────────────────────────────
    roles_map = {
        "sales": ("Sales", SALES_AGENT_PROMPT, bot_tab_sales),
        "support": ("Support", SUPPORT_AGENT_PROMPT, bot_tab_support),
        "care": ("Care", CARE_AGENT_PROMPT, bot_tab_care)
    }

    # Render Bot Tabs
    for role_key, (role_name, system_instr, tab_obj) in roles_map.items():
        with tab_obj:
            st.write(f"**FlowPilot {role_name} Workspace**")
            
            # Show if customer is handed off to human
            is_handed_off = c_id in st.session_state.handoff_queue and len(st.session_state.handoff_queue[c_id]) > 0
            if is_handed_off:
                st.warning(f"⚠️ Live Human Agent Handoff active for {active_c_name}. Bot operations are suspended. Go to the Admin dashboard to chat live as a human.")
            
            # Chat history wrapper
            hist_key = f"chat_{role_key}"
            if hist_key not in st.session_state:
                st.session_state[hist_key] = list(st.session_state.chat_history[role_key])
                
            # Message box container
            chat_container = st.container(height=350)
            
            # Print historical messages
            for msg in st.session_state[hist_key]:
                with chat_container.chat_message(msg["role"]):
                    st.write(msg["content"])
                    # Show sentiment analysis on user messages
                    if msg["role"] == "user":
                        sent, score, col_cls = analyze_sentiment(msg["content"])
                        st.markdown(f'<span class="status-pill {col_cls}">Sentiment: {sent} ({int(score*100)}%)</span>', unsafe_allow_html=True)

            # Voice Input logic / Text Input
            # If we received text from voice, append it as prompt
            prompt = ""
            if voice_query_val:
                prompt = voice_query_val
                # Clear voice_query_val to prevent looping on reload
                voice_query_val = ""
            
            # User Prompt Input
            text_prompt = st.chat_input(f"Type a question to the {role_name} Bot...", key=f"input_{role_key}")
            if text_prompt:
                prompt = text_prompt

            if prompt and not is_handed_off:
                # Add user message to history
                st.session_state[hist_key].append({"role": "user", "content": prompt})
                with chat_container.chat_message("user"):
                    st.write(prompt)
                    sent, score, col_cls = analyze_sentiment(prompt)
                    st.markdown(f'<span class="status-pill {col_cls}">Sentiment: {sent} ({int(score*100)}%)</span>', unsafe_allow_html=True)
                    
                    # Update CRM customer sentiment in dataframe
                    st.session_state.crm_data.loc[st.session_state.crm_data["customer_id"] == c_id, "recent_sentiment"] = sent
                    # Recompute churn risk
                    new_risk = predict_churn_risk(st.session_state.crm_data[st.session_state.crm_data["customer_id"] == c_id].iloc[0])
                    st.session_state.crm_data.loc[st.session_state.crm_data["customer_id"] == c_id, "churn_risk"] = new_risk

                # Generate Answer
                with chat_container.chat_message("assistant"):
                    with st.spinner(f"Agent {role_name} is synthesizing response..."):
                        # RAG enhancement: Check if query matches knowledge base (only after RAG page visited)
                        context = ""
                        if "rag_chunks" in st.session_state:
                            from RAG import compute_tfidf, retrieve_top_chunks
                            chunks = st.session_state.rag_chunks
                            if chunks:
                                tfidf_docs = [{"id": c["chunk_id"], "content": c["content"]} for c in chunks]
                                doc_vectors, idf = compute_tfidf(tfidf_docs)
                                results = retrieve_top_chunks(prompt, chunks, doc_vectors, idf, top_n=1)
                                if results:
                                    context = f"\n[RAG Context: {results[0][1]['content']}]"
                                    
                        full_instruction = system_instr + f"\nCustomer context: Name={active_c_name}, Spend=${cust_record['total_spend']:,.0f}, Open Tickets={cust_record['open_tickets']}" + context
                        
                        answer = generate_ai_response(prompt, system_instruction=full_instruction)
                        st.write(answer)
                        
                        # Handle text to speech
                        if voice_enabled:
                            render_voice_speak_widget(answer)
                            
                # Add bot response to history
                st.session_state[hist_key].append({"role": "assistant", "content": answer})
                st.session_state.chat_history[role_key] = list(st.session_state[hist_key])
                
                # Render Explainable AI Block
                reason = get_explainable_ai_reason(prompt, answer, role_key)
                st.markdown("##### 🔍 Explainable AI Reasoning:")
                st.info(reason)
                
                # Check for automatic workflow trigger simulations
                sentiment_lower = sent.lower()
                if "negative" in sentiment_lower:
                    # Generate ticket automatically
                    ticket_id = f"T-{1000 + len(st.session_state.tickets) + 1}"
                    new_ticket = {
                        "ticket_id": ticket_id,
                        "customer_id": c_id,
                        "customer": active_c_name,
                        "category": f"{role_name} Auto-Escalation",
                        "issue": f"Automated ticket created due to negative sentiment message: \"{prompt}\"",
                        "sentiment": sent,
                        "status": "Open",
                        "created_at": time.strftime("%Y-%m-%d %H:%M"),
                        "assignee": "Aria Stark"
                    }
                    st.session_state.tickets.append(new_ticket)
                    st.session_state.crm_data.loc[st.session_state.crm_data["customer_id"] == c_id, "open_tickets"] += 1
                    st.warning(f"⚡ Workflow Trigger: Ticket **{ticket_id}** automatically generated in CRM database due to Negative Sentiment!")

                st.rerun()

            # Actions Row
            st.markdown("---")
            act_col1, act_col2, act_col3 = st.columns([1, 1.2, 1])
            
            with act_col1:
                st.write("**Voice Interaction**")
                # Render Voice Dictation Mic inside Tab
                render_voice_rec_widget()
                
            with act_col2:
                st.write("**Live Agents**")
                if st.button("🚨 Hand off to Human Agent", key=f"ho_{role_key}"):
                    # Initialize handoff transcript
                    st.session_state.handoff_queue[c_id] = [
                        {"role": "user", "content": f"[SYSTEM]: Request human handoff. Last customer statement: \"{st.session_state[hist_key][-1]['content'] if len(st.session_state[hist_key]) > 1 else 'None'}\""}
                    ]
                    st.success("Conversation successfully routed to Live Agent desk queue!")
                    time.sleep(1)
                    st.rerun()
                    
            with act_col3:
                st.write("**Operations Support**")
                if st.button("📧 Draft Follow-up Email", key=f"em_{role_key}"):
                    # Generate draft based on dialogue history
                    dialogue_str = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state[hist_key][-3:]])
                    email_prompt = f"Write a professional customer follow-up email based on this dialogue:\n{dialogue_str}\n\nDraft Email:"
                    email_system = EMAIL_DRAFT_PROMPT
                    
                    with st.spinner("Drafting professional email envelope..."):
                        email_draft = generate_ai_response(email_prompt, system_instruction=email_system)
                        
                    st.markdown("#### Generated Email Draft:")
                    st.text_area("Copy / Edit Email Content", value=email_draft, height=200)
