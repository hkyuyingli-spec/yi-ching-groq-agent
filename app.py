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
from firebase_config import init_firebase, save_reading, save_feedback, get_user_profile
from enigma_engine import select_hexagram, compute_changing_lines, encode_state_to_bits
from hexagram_profiles import HEXAGRAM_PROFILES
from feedback_engine import process_feedback
from utils.translations import TRANSLATIONS
import uuid

# Page Configuration
st.set_page_config(page_title="Yi Ching Ascension AI", page_icon="☰", layout="wide")

# Initialize Firebase
init_firebase()

# Sidebar - Settings & Cultivation
with st.sidebar:
    st.header("⚙️ Settings")
    lang = st.selectbox("🌐 Language / 語言", options=["en", "zh"], format_func=lambda x: "English" if x=="en" else "繁體中文")
    st.session_state.lang = lang
    t = TRANSLATIONS[lang]

# Apply Zen Styles
apply_zen_styles()

st.title(t["title"])
st.markdown(t["subtitle"])

# Initialize session state
if "lang" not in st.session_state:
    st.session_state.lang = "en"
# ... (rest of session state)
    st.session_state.core = IChingCore()
if "ascension" not in st.session_state:
    st.session_state.ascension = AscensionAI()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = "user_" + str(uuid.uuid4())[:8]
if "last_reading_id" not in st.session_state:
    st.session_state.last_reading_id = None
if "last_hex_num" not in st.session_state:
    st.session_state.last_hex_num = None

def render_hexagram_svg(bits: str, title: str):
    # bits is a 6-bit string, bit 0 is bottom line
    svg = f'<svg width="120" height="160" viewBox="0 0 120 160" xmlns="http://www.w3.org/2000/svg" style="background-color: rgba(255,255,255,0.05); border-radius: 10px; padding: 10px;">'
    svg += f'<text x="60" y="20" font-size="12" text-anchor="middle" fill="#D4AF37" font-weight="bold">{title}</text>'
    for i in range(6):
        bit = bits[i]
        y = 130 - (i * 20)
        if bit == "1": # Yang
            svg += f'<rect x="20" y="{y}" width="80" height="10" fill="#D4AF37" rx="2" />'
        else: # Yin
            svg += f'<rect x="20" y="{y}" width="35" height="10" fill="#D4AF37" rx="2" />'
            svg += f'<rect x="65" y="{y}" width="35" height="10" fill="#D4AF37" rx="2" />'
    svg += '</svg>'
    return svg

# Sidebar - Cultivation Progress
# ... (rest of sidebar code stays same until glossary)
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

async def process_consultation(query, is_enigma=False, enigma_data=None):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        prefix = ""
        if is_enigma and enigma_data:
            primary_bits = enigma_data['primary_bits']
            trans_bits = enigma_data['trans_bits']
            primary_hex = HEXAGRAM_PROFILES[primary_bits]
            
            # Display Hexagrams side by side
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(render_hexagram_svg(primary_bits, t["primary_hex"]), unsafe_allow_html=True)
                st.write(f"**#{primary_hex['number']} {primary_hex['name_en']} ({primary_hex['name_zh']})**")
                st.caption(f"{t['theme_label']}: {primary_hex['theme']}")
            
            if trans_bits:
                trans_hex = HEXAGRAM_PROFILES[trans_bits]
                with col2:
                    st.markdown(render_hexagram_svg(trans_bits, t["trans_hex"]), unsafe_allow_html=True)
                    st.write(f"**#{trans_hex['number']} {trans_hex['name_en']}**")
            
            prefix = f"{t['state_encoded']}\n\n"
            
            # Inject hexagram context into query for AscensionAI
            lang_map = {
                "en": "Please respond in English.",
                "id": "Tolong jawab dalam Bahasa Indonesia.",
                "zh": "請用繁體中文回答。"
            }
            lang_instruction = lang_map.get(st.session_state.lang, "Please respond in English.")
            context_query = f"""
            {lang_instruction}
            I Ching Reading for: {query}
            Current User State: {enigma_data['state_summary']}
            Primary Hexagram: #{primary_hex['number']} - {primary_hex['name_en']} ({primary_hex['theme']})
            """
            if trans_bits:
                trans_hex = HEXAGRAM_PROFILES[trans_bits]
                context_query += f"Transformed Hexagram: #{trans_hex['number']} - {trans_hex['name_en']}\n"
            
            query = context_query

        def on_token(token):
            nonlocal full_response
            token_display = full_response + token
            element_icon = get_element_icon(st.session_state.ascension.state.elemental_affinity)
            formatted_response = f"<div class='oracle-response'><h3>{element_icon} {t['oracle_guidance']}</h3>\n\n{prefix}{token_display}▌</div>"
            response_placeholder.markdown(formatted_response, unsafe_allow_html=True)
            full_response += token

        final_text, breakthrough = await st.session_state.ascension.cultivate(query, on_token=on_token)
        
        element_icon = get_element_icon(st.session_state.ascension.state.elemental_affinity)
        final_formatted = f"<div class='oracle-response'><h3>{element_icon} {t['oracle_guidance']}</h3>\n\n{prefix}{final_text}</div>"
        response_placeholder.markdown(final_formatted, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": final_formatted})
        
        # Save reading to Firebase
        if is_enigma and enigma_data:
            reading_id = str(uuid.uuid4())
            st.session_state.last_reading_id = reading_id
            st.session_state.last_hex_num = primary_hex['number']
            
            save_reading({
                "reading_id": reading_id,
                "user_id": st.session_state.user_id,
                "timestamp": time.time(),
                "question": query,
                "hexagram_number": primary_hex['number'],
                "hexagram_name": primary_hex['name_en'],
                "bit_string": primary_bits,
                "changing_lines": enigma_data.get('changing_lines', []),
                "next_hexagram": HEXAGRAM_PROFILES[trans_bits]['number'] if trans_bits else None,
                "oracle_response": final_text,
                "slider_inputs": enigma_data['slider_values']
            })

        if breakthrough:
            st.balloons()
            st.success(f"🎊 BREAKTHROUGH! You have ascended to: **{st.session_state.ascension.state.current_stage}**")
            time.sleep(2)
            st.rerun()

# Consultation Tabs
if len(st.session_state.messages) == 0:
    tab1, tab2 = st.tabs([t["enigma_tab"], t["direct_consult_tab"]])

    with tab1:
        st.write(t["daily_reflection"])
        col1, col2 = st.columns(2)
        with col1:
            energy = st.slider(t["energy"], 1, 5, 3)
            clarity = st.slider(t["clarity"], 1, 5, 3)
            emotional = st.slider(t["emotional"], 1, 5, 3)
        with col2:
            social = st.slider(t["social"], 1, 5, 3)
            direction = st.slider(t["direction"], 1, 5, 3)
            foundation_bool = st.checkbox(t["foundation"], value=True)

        question_enigma = st.text_area(t["relevant_q"], placeholder="...", key="enigma_q")
        
        if st.button(t["consult_btn"], type="primary", use_container_width=True):
# ... rest of the code
            if question_enigma:
                state = {
                    "energy": energy,
                    "clarity": clarity,
                    "emotional": emotional,
                    "social": social,
                    "direction": direction,
                    "foundation": foundation_bool
                }
                user_bits = encode_state_to_bits(state)
                # For simplicity, we'll use a default profile and empty history if not logged in
                user_profile = get_user_profile(st.session_state.user_id)
                history = [] # In a real app, fetch from Firebase
                context = {"time": time.time(), "streak": 0}
                
                selected_bits = select_hexagram(state, user_profile, history, context)
                trans_bits = compute_changing_lines(state)
                
                enigma_data = {
                    "primary_bits": selected_bits,
                    "trans_bits": trans_bits,
                    "slider_values": state,
                    "state_summary": f"Energy:{energy}, Clarity:{clarity}, Emotional:{emotional}, Social:{social}, Direction:{direction}"
                }
                
                asyncio.run(process_consultation(question_enigma, is_enigma=True, enigma_data=enigma_data))

    with tab2:
        question_direct = st.text_area("What is your inquiry?", placeholder="Ask about Feng Shui, Health, or Destiny...", key="direct_q")
        if st.button("Consult the Master", type="primary", use_container_width=True):
            if question_direct:
                asyncio.run(process_consultation(question_direct))

# Feedback Widget
if st.session_state.last_reading_id and len(st.session_state.messages) > 0:
    st.divider()
    with st.expander(t["rate_reading"], expanded=True):
        st.write(t["relevant_q"])
        col_rel1, col_rel2 = st.columns(2)
        is_relevant = col_rel1.button(t["yes"], key="rel_yes", use_container_width=True)
        not_relevant = col_rel2.button(t["not_really"], key="rel_no", use_container_width=True)
        
        if is_relevant or not_relevant:
            relevant = True if is_relevant else False
            st.write(t["clarity_q"])
            clarity_stars = st.select_slider(t["clarity"], options=[1, 2, 3], format_func=lambda x: "⭐" * x)
            
            st.write(t["action_q"])
            action = st.radio(t["action_q"], [t["yes"], t["thinking"], t["no"]], horizontal=True)
            
            journal = st.text_area(t["journal_placeholder"])
            
            if st.button(t["submit_feedback"], use_container_width=True):
                save_feedback(st.session_state.last_reading_id, {
                    "relevant": relevant,
                    "clarity_stars": clarity_stars,
                    "action_taken": action,
                    "journal": journal,
                    "timestamp": time.time()
                })
                # Update user profile weights
                process_feedback(st.session_state.user_id, st.session_state.last_hex_num, relevant, clarity_stars)
                st.success(t["feedback_success"])
                st.session_state.last_reading_id = None # Clear after submit

# Follow-up Chat
if len(st.session_state.messages) > 0:
    if prompt := st.chat_input("Continue your cultivation..."):
        asyncio.run(process_consultation(prompt))


