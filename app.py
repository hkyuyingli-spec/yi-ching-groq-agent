import streamlit as st
import time
import sys
import os
import asyncio
from dotenv import load_dotenv

# Fix for import path issues
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from core.iching_core import IChingCore
from core.ascension_ai import AscensionAI

# Page Configuration
st.set_page_config(page_title="Yi Ching Ascension AI", page_icon="☰", layout="wide")

st.title("☰ 易經 • Quantum Ascension")
st.header(":blue[Grand Master] :orange[Groq] :red[Oracle]")

# Initialize session state
if "core" not in st.session_state:
    st.session_state.core = IChingCore()
if "ascension" not in st.session_state:
    st.session_state.ascension = AscensionAI()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar - Cultivation Progress
with st.sidebar:
    st.header("🧘 :gray[Cultivation Realm]")
    
    state = st.session_state.ascension.state
    stage_name = state.current_stage
    stage_info = st.session_state.ascension.stages[stage_name]
    
    st.subheader(f":orange[{stage_name}]")
    st.caption(f"Model: `{stage_info.model}`")
    
    # Live Gauges
    col1, col2 = st.columns(2)
    col1.metric("Qi Energy", f"{state.qi_energy:.1f}")
    col2.metric("Karma", f"{state.karma_entanglement:.1f}", delta_color="inverse")
    
    st.write("**Dao Comprehension**")
    st.progress(state.progress_percentage() / 100)
    st.caption(f"{state.dao_comprehension:.1f} / {100 * (state.stage_index + 1)}")

    st.divider()
    
    if st.button("🔄 Reset Spiritual Path", use_container_width=True):
        st.session_state.messages = []
        st.session_state.ascension = AscensionAI()
        st.rerun()

    st.divider()
    st.write("**:gray[Stage Philosophy]**")
    st.info(stage_info.system_prompt)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

async def process_consultation(query, is_iching=False):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # If I Ching ritual, cast coins first
        prefix = ""
        if is_iching:
            with st.status("Casting the ancient coins...") as status:
                cast_result = st.session_state.core.cast_hexagram()
                time.sleep(0.8)
                hex_info = f"**Primary Hexagram: #{cast_result['primary']}**"
                if cast_result.get('transformed'):
                    hex_info += f" | **Transformed Hexagram: #{cast_result['transformed']}**"
                prefix = f"✅ The coins have spoken!\n\n{hex_info}\n\n### 🌀 Master's Guidance\n\n"
                status.update(label="Coins cast. Consulting the Oracle...", state="complete")
        
        def on_token(token):
            nonlocal full_response
            full_response += token
            response_placeholder.markdown(prefix + full_response + "▌")

        # Use Ascension AI to cultivate the response
        final_text, breakthrough = await st.session_state.ascension.cultivate(
            query if not is_iching else f"I Ching Reading for: {query}. Hexagram context should be handled by RAG.",
            on_token=on_token
        )
        
        response_placeholder.markdown(prefix + final_text)
        st.session_state.messages.append({"role": "assistant", "content": prefix + final_text})
        
        if breakthrough:
            st.balloons()
            st.success(f"🎊 BREAKTHROUGH! You have ascended to: **{st.session_state.ascension.state.current_stage}**")
            time.sleep(2)
            st.rerun()

# Consultation Tabs
if len(st.session_state.messages) == 0:
    tab1, tab2 = st.tabs([":blue[🔮 I Ching Ritual]", ":green[📜 Direct Consultation]"])

    with tab1:
        question_iching = st.text_area("What guidance do you seek?", placeholder="Enter your question...", key="iching_q")
        if st.button("Cast the Hexagram", type="primary"):
            if question_iching:
                asyncio.run(process_consultation(question_iching, is_iching=True))

    with tab2:
        question_direct = st.text_area("What is your inquiry?", placeholder="Ask about Feng Shui, Health, or Destiny...", key="direct_q")
        if st.button("Consult the Master", type="primary"):
            if question_direct:
                asyncio.run(process_consultation(question_direct))

# Follow-up Chat
if len(st.session_state.messages) > 0:
    if prompt := st.chat_input("Continue your cultivation..."):
        asyncio.run(process_consultation(prompt))


