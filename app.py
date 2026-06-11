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
from utils.styles import apply_zen_styles, get_element_icon
from utils.glossary import GLOSSARY, STAGES_EXPLAINED, SCORE_INTERPRETATIONS

# Page Configuration
st.set_page_config(page_title="Yi Ching Ascension AI", page_icon="☰", layout="wide")

# Apply Zen Styles
apply_zen_styles()

st.title("☰ 易經 • Quantum Ascension")
st.markdown("### *Divine Wisdom of the Grand Master Oracle*")

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
    
    # Live Gauges with Interpretations
    col1, col2 = st.columns(2)
    
    # Interpret Qi
    qi_label = "Unknown"
    for low, high, label in SCORE_INTERPRETATIONS["qi"]:
        if low <= state.qi_energy < high:
            qi_label = label
            break
            
    # Interpret Karma
    karma_label = "Unknown"
    for low, high, label in SCORE_INTERPRETATIONS["karma"]:
        if low <= state.karma_entanglement < high:
            karma_label = label
            break

    col1.metric("Qi Energy", f"{state.qi_energy:.1f}", help=f"Current State: {qi_label}")
    col2.metric("Karma", f"{state.karma_entanglement:.1f}", delta_color="inverse", help=f"Current State: {karma_label}")
    
    st.caption(f"Spirit Status: **{qi_label}** | Karma Status: **{karma_label}**")
    
    # ML Insights
    st.divider()
    st.write("**:gray[Machine Learning Insights]**")
    if state.sentiment_history:
        last_sentiment = state.sentiment_history[-1]
        sentiment_label = "Neutral 😐"
        if last_sentiment > 0.3: sentiment_label = "Harmonious 😊"
        elif last_sentiment < -0.3: sentiment_label = "Conflicted 😠"
        st.caption(f"Last Intent Sentiment: **{sentiment_label}** ({last_sentiment:.2f})")
    
    if state.elemental_affinity != "Neutral":
        st.caption(f"Current Elemental Affinity: **{state.elemental_affinity}**")
    
    st.write("**Dao Comprehension**")
    st.progress(state.progress_percentage() / 100)
    st.caption(f"{state.dao_comprehension:.1f} / {100 * (state.stage_index + 1)}")

    st.divider()
    with st.expander("📜 **Glossary of the Path**"):
        for term, definition in GLOSSARY.items():
            st.write(f"**{term}**: {definition}")
        st.divider()
        st.write("**:orange[Cultivation Realms]**")
        for realm, desc in STAGES_EXPLAINED.items():
            st.write(f"*{realm}*: {desc}")

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
        
        # If I Ching ritual, cast coins with ritualistic animation
        prefix = ""
        if is_iching:
            ritual_container = st.container()
            with ritual_container:
                st.markdown("### 🏺 *The Ritual Begins*")
                progress_ritual = st.empty()
                
                # Cast hexagram
                cast_result = st.session_state.core.cast_hexagram()
                
                # Animate line by line
                for i, line in enumerate(cast_result['lines']):
                    msg = f"Casting line {i+1}... **{line['symbol']}** ({line['type']})"
                    progress_ritual.markdown(f"<div class='ritual-line'>{msg}</div>", unsafe_allow_html=True)
                    time.sleep(0.4)
                
                time.sleep(0.5)
                hex_info = f"**Primary Hexagram: #{cast_result['primary']}**"
                if cast_result.get('transformed'):
                    hex_info += f" | **Transformed Hexagram: #{cast_result['transformed']}**"
                
                prefix = f"✅ **The coins have settled.**\n\n{hex_info}\n\n"
                ritual_container.empty() # Clear ritual animation

        def on_token(token):
            nonlocal full_response
            token_display = full_response + token
            # Use custom container for the response
            element_icon = get_element_icon(st.session_state.ascension.state.elemental_affinity)
            formatted_response = f"<div class='oracle-response'><h3>{element_icon} Oracle's Guidance</h3>\n\n{prefix}{token_display}▌</div>"
            response_placeholder.markdown(formatted_response, unsafe_allow_html=True)
            full_response += token

        # Use Ascension AI to cultivate the response
        final_text, breakthrough = await st.session_state.ascension.cultivate(
            query if not is_iching else f"I Ching Reading for: {query}. Hexagram context should be handled by RAG.",
            on_token=on_token
        )
        
        element_icon = get_element_icon(st.session_state.ascension.state.elemental_affinity)
        final_formatted = f"<div class='oracle-response'><h3>{element_icon} Oracle's Guidance</h3>\n\n{prefix}{final_text}</div>"
        response_placeholder.markdown(final_formatted, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": final_formatted})
        
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


