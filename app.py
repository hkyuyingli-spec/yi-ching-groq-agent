import streamlit as st
import time
import sys
import os
import asyncio
from dotenv import load_dotenv
import uuid
import datetime

# Fix for import path issues
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from core.iching_core import IChingCore
from core.ascension_ai import AscensionAI
from utils.styles import apply_zen_styles, get_element_icon, card_begin, card_end
from utils.glossary import GLOSSARY, STAGES_EXPLAINED, SCORE_INTERPRETATIONS
from firebase_config import init_firebase, save_reading, save_feedback, get_user_profile, get_db, get_reading_history
from enigma_engine import select_hexagram, compute_changing_lines, encode_state_to_bits
from hexagram_profiles import HEXAGRAM_PROFILES
from feedback_engine import process_feedback
from utils.translations import TRANSLATIONS

# Page Configuration
st.set_page_config(page_title="Yi Ching Ascension AI", page_icon="☰", layout="wide")

# Initialize Firebase
init_firebase()

# Initialize session state
if "core" not in st.session_state:
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
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# Sidebar Navigation
with st.sidebar:
    st.title("📂 Navigation")
    lang_options = ["en", "id", "zh"]
    lang_display = {"en": "English", "id": "Bahasa Indonesia", "zh": "繁體中文"}
    lang = st.selectbox("🌐 Language", options=lang_options, format_func=lambda x: lang_display[x], index=lang_options.index(st.session_state.lang))
    st.session_state.lang = lang
    t = TRANSLATIONS[lang]
    
    st.divider()
    
    menu = st.radio(
        "Menu",
        [t["nav_home"], t["nav_oracle"], t["nav_history"], t["nav_examples"], t["nav_how"], t["nav_settings"]],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.header(t["sidebar_header"])
    state = st.session_state.ascension.state
    st.subheader(f":orange[{state.current_stage}]")
    st.progress(state.progress_percentage() / 100)

# Helper Functions
def render_hexagram_svg(bits: str, title: str):
    # Professional hexagram display
    svg = f'<svg width="140" height="180" viewBox="0 0 140 180" xmlns="http://www.w3.org/2000/svg" style="background-color: #FCF9F2; border-radius: 12px; border: 1px solid #E8E4D9; padding: 15px;">'
    svg += f'<text x="70" y="25" font-family=\'Lora\', serif font-size="14" text-anchor="middle" fill="#4A3728" font-weight="600">{title}</text>'
    for i in range(6):
        bit = bits[i]
        y = 150 - (i * 20)
        if bit == "1": # Yang
            svg += f'<rect x="25" y="{y}" width="90" height="12" fill="#4A3728" rx="3" />'
        else: # Yin
            svg += f'<rect x="25" y="{y}" width="40" height="12" fill="#4A3728" rx="3" />'
            svg += f'<rect x="75" y="{y}" width="40" height="12" fill="#4A3728" rx="3" />'
    svg += '</svg>'
    return svg

def parse_structured_response(text: str):
    # Look for common markers or just return as is if not structured
    markers = [t["the_judgment"], t["the_image"], t["changing_lines"], t["master_strategy"]]
    if any(m in text for m in markers):
        return text # Already structured by AI
    return text

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
            
            # Professional Side-by-Side Hexagram Display
            cols = st.columns(2)
            with cols[0]:
                st.markdown(render_hexagram_svg(primary_bits, t["primary_hex"]), unsafe_allow_html=True)
                st.write(f"**#{primary_hex['number']} {primary_hex['name_en']}**")
                st.caption(f"{t['theme_label']}: {primary_hex['theme']}")
            
            if trans_bits:
                trans_hex = HEXAGRAM_PROFILES[trans_bits]
                with cols[1]:
                    st.markdown(render_hexagram_svg(trans_bits, t["trans_hex"]), unsafe_allow_html=True)
                    st.write(f"**#{trans_hex['number']} {trans_hex['name_en']}**")
            
            prefix = f"{t['state_encoded']}\n\n"
            
            # Enforce structured output in the AI prompt
            lang_map = {"en": "English", "id": "Bahasa Indonesia", "zh": "Traditional Chinese"}
            target_lang = lang_map.get(st.session_state.lang, "English")
            
            query = f"""
            Please respond in {target_lang}.
            Provide a structured I Ching Reading for: {query}
            
            User State: {enigma_data['state_summary']}
            Primary Hexagram: #{primary_hex['number']} - {primary_hex['name_en']}
            
            Structure your response exactly with these headers:
            ### 📜 {t['the_judgment']}
            ...
            ### 🖼️ {t['the_image']}
            ...
            ### ⚡ {t['changing_lines']}
            ...
            ### 🧘 {t['master_strategy']}
            ...
            """
            if trans_bits:
                query += f"\nTransformed Hexagram: #{HEXAGRAM_PROFILES[trans_bits]['number']}"

        def on_token(token):
            nonlocal full_response
            full_response += token
            element_icon = get_element_icon(st.session_state.ascension.state.elemental_affinity)
            response_placeholder.markdown(f"<div class='oracle-response'><h3>{element_icon} {t['oracle_guidance']}</h3>\n\n{prefix}{full_response}▌</div>", unsafe_allow_html=True)

        final_text, breakthrough = await st.session_state.ascension.cultivate(query, on_token=on_token)
        element_icon = get_element_icon(st.session_state.ascension.state.elemental_affinity)
        response_placeholder.markdown(f"<div class='oracle-response'><h3>{element_icon} {t['oracle_guidance']}</h3>\n\n{prefix}{final_text}</div>", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": final_text})
        
        if is_enigma and enigma_data:
            reading_id = str(uuid.uuid4())
            st.session_state.last_reading_id, st.session_state.last_hex_num = reading_id, primary_hex['number']
            save_reading({
                "reading_id": reading_id,
                "user_id": st.session_state.user_id,
                "timestamp": time.time(),
                "hexagram_number": primary_hex['number'],
                "hexagram_name": primary_hex['name_en'],
                "oracle_response": final_text,
                "state_summary": enigma_data['state_summary']
            })

# Main Content Logic
apply_zen_styles()

if menu == t["nav_home"]:
    st.title(t["title"])
    st.markdown(f'<div class="wisdom-text">{t["subtitle"]}</div>', unsafe_allow_html=True)
    
    # Journey Summary Card with Real-time metrics
    history = get_reading_history(st.session_state.user_id, limit=50)
    readings_count = len(history)
    
    st.markdown(card_begin(t["journey_title"]), unsafe_allow_html=True)
    j_col1, j_col2 = st.columns(2)
    with j_col1:
        st.write(f"📊 **{t['readings_count']}**: {readings_count}")
        st.write(f"✨ **{t['dominant_element']}**: {get_element_icon(state.elemental_affinity)} {state.elemental_affinity}")
    with j_col2:
        st.write(f"🌊 **{t['current_resonance']}**: {70 + (state.qi_energy % 30):.0f}%")
        st.write(f"🏆 **{t['ascension_level']}**: {state.current_stage}")
    st.markdown(card_end(), unsafe_allow_html=True)

    # Qi & Karma Gauges
    st.markdown(card_begin(), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.metric("Qi Energy", f"{state.qi_energy:.1f}")
    col2.metric("Karma", f"{state.karma_entanglement:.1f}", delta_color="inverse")
    st.markdown(card_end(), unsafe_allow_html=True)
    
    st.info(f"💡 **Daily Tip**: {GLOSSARY.get('Wu Wei', 'Patience is the root of wisdom.')}")

elif menu == t["nav_oracle"]:
    st.title(t["nav_oracle"])
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(f'<div class="interpretation">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(message["content"])
    
    if len(st.session_state.messages) == 0:
        tab1, tab2 = st.tabs([t["enigma_tab"], t["direct_consult_tab"]])
        with tab1:
            st.markdown(card_begin(t["enigma_tab"]), unsafe_allow_html=True)
            st.write(t["daily_reflection"])
            c1, c2 = st.columns(2)
            energy = c1.slider(t["energy"], 1, 5, 3)
            clarity = c1.slider(t["clarity"], 1, 5, 3)
            emotional = c1.slider(t["emotional"], 1, 5, 3)
            social = c2.slider(t["social"], 1, 5, 3)
            direction = c2.slider(t["direction"], 1, 5, 3)
            foundation = c2.checkbox(t["foundation"], value=True)
            q = st.text_area(t["relevant_q"], key="enigma_q")
            if st.button(t["consult_btn"], type="primary", use_container_width=True):
                state_val = {"energy": energy, "clarity": clarity, "emotional": emotional, "social": social, "direction": direction, "foundation": foundation}
                selected = select_hexagram(state_val, get_user_profile(st.session_state.user_id), [], {"time": time.time(), "streak": 0})
                asyncio.run(process_consultation(q, is_enigma=True, enigma_data={"primary_bits": selected, "trans_bits": compute_changing_lines(state_val), "state_summary": str(state_val)}))
            st.markdown(card_end(), unsafe_allow_html=True)
            
        with tab2:
            st.markdown(card_begin(t["direct_consult_tab"]), unsafe_allow_html=True)
            q_dir = st.text_area("What is your inquiry?", key="direct_q")
            if st.button("Consult the Master", type="primary", use_container_width=True): 
                asyncio.run(process_consultation(q_dir))
            st.markdown(card_end(), unsafe_allow_html=True)

    if st.session_state.last_reading_id and len(st.session_state.messages) > 0:
        with st.expander(t["rate_reading"], expanded=True):
            if st.button(t["yes"], use_container_width=True):
                process_feedback(st.session_state.user_id, st.session_state.last_hex_num, True, 3)
                st.success(t["feedback_success"])
                st.session_state.last_reading_id = None
    
    if len(st.session_state.messages) > 0:
        if prompt := st.chat_input("Continue your cultivation..."): 
            asyncio.run(process_consultation(prompt))

elif menu == t["nav_history"]:
    st.title(t["history_title"])
    history = get_reading_history(st.session_state.user_id)
    if not history:
        st.info("Your spiritual path is just beginning. No readings found yet.")
    else:
        for entry in history:
            with st.expander(f"📜 {datetime.datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M')} | Hexagram #{entry.get('hexagram_number')}"):
                st.markdown(f"**Question**: {entry.get('question', 'Direct Inquiry')}")
                st.markdown(f'<div class="interpretation">{entry.get("oracle_response", "")}</div>', unsafe_allow_html=True)

elif menu == t["nav_examples"]:
    st.title(t["nav_examples"])
    st.markdown(card_begin(t["nav_examples"]), unsafe_allow_html=True)
    for bits, data in list(HEXAGRAM_PROFILES.items())[:10]:
        st.markdown(f'<div class="wisdom-text">**#{data["number"]} {data["name_en"]} ({data["name_zh"]})**: {data["short_meaning"]}</div>', unsafe_allow_html=True)
    st.markdown(card_end(), unsafe_allow_html=True)

elif menu == t["nav_how"]:
    st.title(t["nav_how"])
    st.markdown(card_begin(), unsafe_allow_html=True)
    with open("USER_GUIDE.md", "r", encoding="utf-8") as f:
        st.markdown(f'<div class="wisdom-text">{f.read()}</div>', unsafe_allow_html=True)
    st.markdown(card_end(), unsafe_allow_html=True)

elif menu == t["nav_settings"]:
    st.title(t["nav_settings"])
    st.markdown(card_begin(), unsafe_allow_html=True)
    st.write(f"**User ID**: `{st.session_state.user_id}`")
    if st.button(t["reset_btn"], use_container_width=True):
        st.session_state.messages = []
        st.session_state.ascension = AscensionAI()
        st.rerun()
    st.markdown(card_end(), unsafe_allow_html=True)
