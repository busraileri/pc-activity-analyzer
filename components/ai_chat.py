import streamlit as st

def render_ai_chat():

    st.subheader("💬 Ask About Your Usage")
    st.markdown("**Quick Questions:**")

    # Quick questions - set query with session state
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📱 What app did I use most today?", key="q1_stable"):
            st.session_state["active_query"] = "What app did I use most today?"
            
        if st.button("⏰ What are my most active hours?", key="q2_stable"):
            st.session_state["active_query"] = "What are my most active hours?"
            
    with col2:
        if st.button("📊 How productive was I this week?", key="q3_stable"):
            st.session_state["active_query"] = "How productive was I this week?"
            
        if st.button("🎯 Which day was I most focused?", key="q4_stable"):
            st.session_state["active_query"] = "Which day was I most focused?"

    # Text input
    user_query = st.text_input(
        "💭 Ask me anything:",
        value=st.session_state.get("active_query", ""),
        placeholder="e.g., How much time did I spend on work apps?",
        key="user_input_stable"
    )

    # Clear button
    if st.button("🗑️ Clear Query", key="clear_stable"):
        if "active_query" in st.session_state:
            del st.session_state["active_query"]
        st.rerun()

    # Process query
    if user_query:
        # Chatbot operations
        try:
            from utils.instance import get_rag_instance
            
            # Loading state
            with st.spinner("🤖 AI is analyzing your data..."):
                chatbot = get_rag_instance()
                response = chatbot.answer_question(user_query)
            
            # Response
            st.success(f"**AI Assistant:** {response}")
            
        except Exception as e:
            st.error(f"❌ Error processing your question: {str(e)}")
            st.info("💡 Try rephrasing your question or check if your data is loaded correctly.")

