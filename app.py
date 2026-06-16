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
from utils.translations import TRANSLATIONS, translate

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
    st.title(f"📂 {translate('nav_home', st.session_state.lang).split()[1]} Navigation") # Simplified title
    lang_options = ["en", "id", "zh"]
    lang_display = {"en": "English", "id": "Bahasa Indonesia", "zh": "繁體中文"}
    lang = st.selectbox(f"🌐 {translate('lang_label', st.session_state.lang)}", options=lang_options, format_func=lambda x: lang_display[x], index=lang_options.index(st.session_state.lang))
    st.session_state.lang = lang
    
    st.divider()
    
    menu = st.radio(
        "Menu",
        [
            translate("nav_home", lang),
            translate("nav_oracle", lang),
            translate("nav_history", lang),
            translate("nav_examples", lang),
            translate("nav_how", lang),
            translate("nav_settings", lang)
        ],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.header(translate("sidebar_header", lang))
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

async def process_consultation(query, is_enigma=False, enigma_data=None):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        prefix = ""
        lang = st.session_state.lang
        
        if is_enigma and enigma_data:
            primary_bits = enigma_data['primary_bits']
            trans_bits = enigma_data['trans_bits']
            primary_hex = HEXAGRAM_PROFILES[primary_bits]
            
            # Professional Side-by-Side Hexagram Display
            cols = st.columns(2)
            with cols[0]:
                st.markdown(render_hexagram_svg(primary_bits, translate("primary_hex", lang)), unsafe_allow_html=True)
                st.write(f"**#{primary_hex['number']} {primary_hex['name_en']}**")
                st.caption(f"{translate('theme_label', lang)}: {primary_hex['theme']}")
            
            if trans_bits:
                trans_hex = HEXAGRAM_PROFILES[trans_bits]
                with cols[1]:
                    st.markdown(render_hexagram_svg(trans_bits, translate("trans_hex", lang)), unsafe_allow_html=True)
                    st.write(f"**#{trans_hex['number']} {trans_hex['name_en']}**")
            
            prefix = f"{translate('state_encoded', lang)}\n\n"
            
            # Enforce structured output in the AI prompt
            lang_map = {"en": "English", "id": "Bahasa Indonesia", "zh": "Traditional Chinese"}
            target_lang = lang_map.get(lang, "English")
            
            query = f"""
            Please respond in {target_lang}.
            Provide a structured I Ching Reading for: {query}
            
            User State: {enigma_data['state_summary']}
            Primary Hexagram: #{primary_hex['number']} - {primary_hex['name_en']}
            
            Structure your response exactly with these headers:
            ### 📜 {translate('the_judgment', lang)}
            ...
            ### 🖼️ {translate('the_image', lang)}
            ...
            ### ⚡ {translate('changing_lines', lang)}
            ...
            ### 🧘 {translate('master_strategy', lang)}
            ...
            """
            if trans_bits:
                query += f"\nTransformed Hexagram: #{HEXAGRAM_PROFILES[trans_bits]['number']}"

        def on_token(token):
            nonlocal full_response
            full_response += token
            element_icon = get_element_icon(st.session_state.ascension.state.elemental_affinity)
            response_placeholder.markdown(f"<div class='oracle-response'><h3>{element_icon} {translate('oracle_guidance', lang)}</h3>\n\n{prefix}{full_response}▌</div>", unsafe_allow_html=True)

        final_text, breakthrough = await st.session_state.ascension.cultivate(query, on_token=on_token)
        element_icon = get_element_icon(st.session_state.ascension.state.elemental_affinity)
        response_placeholder.markdown(f"<div class='oracle-response'><h3>{element_icon} {translate('oracle_guidance', lang)}</h3>\n\n{prefix}{final_text}</div>", unsafe_allow_html=True)
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
lang = st.session_state.lang

if menu == translate("nav_home", lang):
    st.title(translate("title", lang))
    st.markdown(f'<div class="wisdom-text">{translate("subtitle", lang)}</div>', unsafe_allow_html=True)
    
    # Journey Summary Card with Real-time metrics
    history = get_reading_history(st.session_state.user_id, limit=50)
    readings_count = len(history)
    
    st.markdown(card_begin(translate("journey_title", lang)), unsafe_allow_html=True)
    j_col1, j_col2 = st.columns(2)
    with j_col1:
        st.write(f"📊 **{translate('readings_count', lang)}**: {readings_count}")
        st.write(f"✨ **{translate('dominant_element', lang)}**: {get_element_icon(state.elemental_affinity)} {state.elemental_affinity}")
    with j_col2:
        st.write(f"🌊 **{translate('current_resonance', lang)}**: {70 + (state.qi_energy % 30):.0f}%")
        st.write(f"🏆 **{translate('ascension_level', lang)}**: {state.current_stage}")
    st.markdown(card_end(), unsafe_allow_html=True)

    # Qi & Karma Gauges
    st.markdown(card_begin(), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.metric("Qi Energy", f"{state.qi_energy:.1f}")
    col2.metric("Karma", f"{state.karma_entanglement:.1f}", delta_color="inverse")
    st.markdown(card_end(), unsafe_allow_html=True)
    
    st.info(f"💡 **{translate('daily_tip', lang)}**: {GLOSSARY.get('Wu Wei', 'Patience is the root of wisdom.')}")

elif menu == translate("nav_oracle", lang):
    st.title(translate("nav_oracle", lang))
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(f'<div class="interpretation">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(message["content"])
    
    if len(st.session_state.messages) == 0:
        tab1, tab2 = st.tabs([translate("enigma_tab", lang), translate("direct_consult_tab", lang)])
        with tab1:
            st.markdown(card_begin(translate("enigma_tab", lang)), unsafe_allow_html=True)
            st.write(translate("daily_reflection", lang))
            c1, c2 = st.columns(2)
            energy = c1.slider(translate("energy", lang), 1, 5, 3)
            clarity = c1.slider(translate("clarity", lang), 1, 5, 3)
            emotional = c1.slider(translate("emotional", lang), 1, 5, 3)
            social = c2.slider(translate("social", lang), 1, 5, 3)
            direction = c2.slider(translate("direction", lang), 1, 5, 3)
            foundation = c2.checkbox(translate("foundation", lang), value=True)
            q = st.text_area(translate("inquiry_placeholder", lang), key="enigma_q")
            if st.button(translate("consult_btn", lang), type="primary", use_container_width=True):
                state_val = {"energy": energy, "clarity": clarity, "emotional": emotional, "social": social, "direction": direction, "foundation": foundation}
                selected = select_hexagram(state_val, get_user_profile(st.session_state.user_id), [], {"time": time.time(), "streak": 0})
                asyncio.run(process_consultation(q, is_enigma=True, enigma_data={"primary_bits": selected, "trans_bits": compute_changing_lines(state_val), "state_summary": str(state_val)}))
            st.markdown(card_end(), unsafe_allow_html=True)
            
        with tab2:
            st.markdown(card_begin(translate("direct_consult_tab", lang)), unsafe_allow_html=True)
            q_dir = st.text_area(translate("direct_inquiry_placeholder", lang), key="direct_q")
            if st.button(translate("direct_consult_btn", lang), type="primary", use_container_width=True): 
                asyncio.run(process_consultation(q_dir))
            st.markdown(card_end(), unsafe_allow_html=True)

    if st.session_state.last_reading_id and len(st.session_state.messages) > 0:
        with st.expander(translate("rate_reading", lang), expanded=True):
            st.write(translate("relevant_q", lang))
            col_rel1, col_rel2 = st.columns(2)
            if col_rel1.button(translate("yes", lang), use_container_width=True):
                process_feedback(st.session_state.user_id, st.session_state.last_hex_num, True, 3)
                st.success(translate("feedback_success", lang))
                st.session_state.last_reading_id = None
            if col_rel2.button(translate("not_really", lang), use_container_width=True):
                process_feedback(st.session_state.user_id, st.session_state.last_hex_num, False, 1)
                st.success(translate("feedback_success", lang))
                st.session_state.last_reading_id = None
    
    if len(st.session_state.messages) > 0:
        if prompt := st.chat_input(translate("continue_cultivation", lang)): 
            asyncio.run(process_consultation(prompt))

elif menu == translate("nav_history", lang):
    st.title(translate("history_title", lang))
    history = get_reading_history(st.session_state.user_id)
    if not history:
        st.info(translate("no_history", lang))
    else:
        for entry in history:
            date_str = datetime.datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M')
            expander_label = translate("history_expander", lang).format(date=date_str, num=entry.get('hexagram_number'))
            with st.expander(expander_label):
                st.markdown(f"**{translate('inquiry_placeholder', lang)}**: {entry.get('question', 'Direct Inquiry')}")
                st.markdown(f'<div class="interpretation">{entry.get("oracle_response", "")}</div>', unsafe_allow_html=True)

elif menu == translate("nav_examples", lang):
    st.title(translate("nav_examples", lang))
    st.markdown(card_begin(translate("nav_examples", lang)), unsafe_allow_html=True)
    st.write(translate("examples_desc", lang))
    for bits, data in list(HEXAGRAM_PROFILES.items())[:10]:
        st.markdown(f'<div class="wisdom-text">**#{data["number"]} {data["name_en"]} ({data["name_zh"]})**: {data["short_meaning"]}</div>', unsafe_allow_html=True)
    st.markdown(card_end(), unsafe_allow_html=True)

elif menu == translate("nav_how", lang):
    st.title(translate("nav_how", lang))
    st.markdown(card_begin(), unsafe_allow_html=True)
    # Load localized user guide if available, else default to English
    guide_map = {"en": "USER_GUIDE.md", "id": "USER_GUIDE_KIDS_ID.md", "zh": "USER_GUIDE_KIDS_ZH.md"} # Using kids versions for simplicity in this review
    guide_file = guide_map.get(lang, "USER_GUIDE.md")
    try:
        with open(guide_file, "r", encoding="utf-8") as f:
            st.markdown(f'<div class="wisdom-text">{f.read()}</div>', unsafe_allow_html=True)
    except:
        st.error("Guide not found.")
    st.markdown(card_end(), unsafe_allow_html=True)

elif menu == translate("nav_settings", lang):
    st.title(translate("nav_settings", lang))
    st.markdown(card_begin(), unsafe_allow_html=True)
    st.write(f"**{translate('user_id_label', lang)}**: `{st.session_state.user_id}`")
    if st.button(translate("reset_btn", lang), use_container_width=True):
        st.session_state.messages = []
        st.session_state.ascension = AscensionAI()
        st.rerun()
    st.markdown(card_end(), unsafe_allow_html=True)
