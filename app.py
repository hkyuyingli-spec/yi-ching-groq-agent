import asyncio
import datetime
import os
import sys
import time
import uuid

import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from core.ascension_ai import AscensionAI, GroqManager
from core.iching_core import IChingCore
from feedback_engine import process_feedback
from firebase_config import get_reading_history, get_user_profile, init_firebase, save_reading
from hexagram_profiles import HEXAGRAM_PROFILES
from utils.glossary import GLOSSARY
from utils.styles import apply_zen_styles, card_begin, card_end
from utils.translations import translate
from core.fengshui import describe_hexagram_feng_shui

st.set_page_config(page_title="Yi Ching Oracle", page_icon="☰", layout="wide")
init_firebase()

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
if "active_reading" not in st.session_state:
    st.session_state.active_reading = None
if "suggestion_chips" not in st.session_state:
    st.session_state.suggestion_chips = []


def generate_suggestion_chips(active_reading: dict) -> list[str]:
    if not active_reading or "primary_hex" not in active_reading:
        return []
    p_hex = active_reading["primary_hex"]
    c_lines = active_reading.get("changing_lines", [])

    chip1 = f"How should I apply the theme of '{p_hex['theme']}' to my situation?"
    if c_lines:
        lines_str = ", ".join([str(l) for l in c_lines])
        chip2 = f"What specific advice do changing line(s) {lines_str} provide?"
    else:
        chip2 = f"What specific actions should I avoid under #{p_hex['number']} {p_hex['name_en']}?"
    chip3 = f"What is the recommended timing and strategy for {p_hex['name_en']}?"

    return [chip1, chip2, chip3]


def render_assistant_message(content: str):
    marker = "### 🔍 Detailed Classical Analysis"
    if marker in content:
        parts = content.split(marker, 1)
        st.markdown(parts[0])
        with st.expander("Read full classical analysis", expanded=False):
            st.markdown(marker + parts[1])
    else:
        st.markdown(content)


def render_hexagram_svg(bits: str, title: str) -> str:
    svg = "<svg width='140' height='180' viewBox='0 0 140 180' xmlns='http://www.w3.org/2000/svg' style='background-color:#FCF9F2;border-radius:12px;border:1px solid #E8E4D9;padding:15px;'>"
    svg += f"<text x='70' y='25' font-family='serif' font-size='14' text-anchor='middle' fill='#4A3728' font-weight='600'>{title}</text>"
    for index, bit in enumerate(bits):
        y = 150 - (index * 20)
        if bit == "1":
            svg += f"<rect x='25' y='{y}' width='90' height='12' fill='#4A3728' rx='3' />"
        else:
            svg += f"<rect x='25' y='{y}' width='40' height='12' fill='#4A3728' rx='3' />"
            svg += f"<rect x='75' y='{y}' width='40' height='12' fill='#4A3728' rx='3' />"
    return svg + "</svg>"


async def process_consultation(query: str, is_reading: bool = False, reading_data: dict | None = None) -> None:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        prefix = ""
        lang = st.session_state.lang

        if is_reading and reading_data:
            primary_bits = reading_data["primary_bits"]
            trans_bits = reading_data.get("transformed_bits")
            primary_hex = HEXAGRAM_PROFILES[primary_bits]
            trans_hex = HEXAGRAM_PROFILES[trans_bits] if trans_bits else None

            st.session_state.active_reading = {
                "primary_bits": primary_bits,
                "transformed_bits": trans_bits,
                "primary_hex": primary_hex,
                "transformed_hex": trans_hex,
                "changing_lines": reading_data.get("changing_lines", []),
                "intention_summary": reading_data.get("intention_summary", ""),
            }
            st.session_state.suggestion_chips = generate_suggestion_chips(st.session_state.active_reading)

            feng_shui_summary = describe_hexagram_feng_shui(primary_hex)
            columns = st.columns(2)
            with columns[0]:
                st.markdown(render_hexagram_svg(primary_bits, translate("primary_hex", lang)), unsafe_allow_html=True)
                st.write(f"#{primary_hex['number']} {primary_hex['name_en']}")
                st.caption(f"{translate('theme_label', lang)}: {primary_hex['theme']}")
                st.caption(feng_shui_summary["summary"])
            if trans_hex:
                with columns[1]:
                    st.markdown(render_hexagram_svg(trans_bits, translate("trans_hex", lang)), unsafe_allow_html=True)
                    st.write(f"#{trans_hex['number']} {trans_hex['name_en']}")

            prefix = "The coins have been cast.\n\n"
            language_names = {"en": "English", "id": "Bahasa Indonesia", "zh": "Traditional Chinese"}
            prompt = f"""
Please respond in {language_names.get(lang, 'English')}.
Provide a structured I Ching reading for: {query if query else 'General Guidance'}

Intention context (it did not determine this cast): {reading_data['intention_summary']}
Primary Hexagram: #{primary_hex['number']} - {primary_hex['name_en']}
"""
            if trans_bits:
                prompt += f"\nChanging lines: {reading_data['changing_lines']}"
                prompt += f"\nTransformed Hexagram: #{trans_hex['number']} - {trans_hex['name_en']}"

            prompt += f"\n\nFeng Shui Summary:\n{feng_shui_summary['summary']}"
        else:
            prompt = query

        def on_token(token: str) -> None:
            nonlocal full_response
            full_response += token
            response_placeholder.markdown(
                f"<div class='oracle-response'><h3>{translate('oracle_guidance', lang)}</h3>\n\n{prefix}{full_response}</div>",
                unsafe_allow_html=True,
            )

        active = st.session_state.get("active_reading")
        if active:
            final_text = await st.session_state.ascension.respond_to_reading(
                primary_hex_number=active["primary_hex"]["number"],
                transformed_hex_number=active["transformed_hex"]["number"] if active.get("transformed_hex") else None,
                query=prompt,
                on_token=on_token,
            )
        else:
            final_text = await st.session_state.ascension.respond(prompt, on_token=on_token)

        response_placeholder.empty()
        full_content = f"{prefix}{final_text}"
        render_assistant_message(full_content)
        st.session_state.messages.append({"role": "assistant", "content": full_content})

        if is_reading and reading_data:
            reading_id = str(uuid.uuid4())
            st.session_state.last_reading_id = reading_id
            st.session_state.last_hex_num = primary_hex["number"]
            save_reading({
                "reading_id": reading_id,
                "user_id": st.session_state.user_id,
                "timestamp": time.time(),
                "hexagram_number": primary_hex["number"],
                "hexagram_name": primary_hex["name_en"],
                "oracle_response": final_text,
                "intention_summary": reading_data["intention_summary"],
                "changing_lines": reading_data["changing_lines"],
            })


apply_zen_styles()
lang = st.session_state.lang

if menu == translate("nav_home", lang):
    st.title(translate("title", lang))
    st.markdown(f"<div class='wisdom-text'>{translate('subtitle', lang)}</div>", unsafe_allow_html=True)
    history = get_reading_history(st.session_state.user_id, limit=50)
    st.markdown(card_begin(translate("journey_title", lang)), unsafe_allow_html=True)
    st.write(f"Readings: {len(history)}")
    st.markdown(card_end(), unsafe_allow_html=True)
    st.info(f"{translate('daily_tip', lang)}: {GLOSSARY.get('Wu Wei', 'Patience is the root of wisdom.')}")

elif menu == translate("nav_oracle", lang):
    st.title(translate("nav_oracle", lang))

    if st.session_state.get("active_reading"):
        active = st.session_state.active_reading
        p_hex = active["primary_hex"]
        t_hex = active.get("transformed_hex")
        banner_md = f"☯ **Active Reading:** #{p_hex['number']} {p_hex['name_en']} ({p_hex['name_zh']}) - *{p_hex['short_meaning']}*"
        if t_hex:
            banner_md += f" &nbsp;➔&nbsp; #{t_hex['number']} {t_hex['name_en']} ({t_hex['name_zh']})"
        st.info(banner_md)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                render_assistant_message(message["content"])
            else:
                st.markdown(message["content"])

    if not st.session_state.messages:
        tab1, tab2 = st.tabs([translate("enigma_tab", lang), translate("direct_consult_tab", lang)])
        with tab1:
            st.markdown(card_begin(translate("enigma_tab", lang)), unsafe_allow_html=True)
            st.write("Optionally set your intention before casting. These answers provide context for the interpretation; they do not determine the hexagram.")
            left, right = st.columns(2)
            energy = left.slider(translate("energy", lang), 1, 5, 3)
            clarity = left.slider(translate("clarity", lang), 1, 5, 3)
            emotional = left.slider(translate("emotional", lang), 1, 5, 3)
            social = right.slider(translate("social", lang), 1, 5, 3)
            direction = right.slider(translate("direction", lang), 1, 5, 3)
            foundation = right.checkbox(translate("foundation", lang), value=True)
            question = st.text_area(translate("inquiry_placeholder", lang), key="enigma_q")
            if st.button("Cast Hexagram", type="primary", use_container_width=True):
                reflection_state = {
                    "energy": energy,
                    "clarity": clarity,
                    "emotional": emotional,
                    "social": social,
                    "direction": direction,
                    "foundation": foundation,
                }
                cast = st.session_state.core.cast_hexagram()
                asyncio.run(process_consultation(
                    question,
                    is_reading=True,
                    reading_data={
                        **cast,
                        "intention_summary": str(reflection_state),
                    },
                ))
                st.rerun()
            st.markdown(card_end(), unsafe_allow_html=True)

        with tab2:
            st.markdown(card_begin(translate("direct_consult_tab", lang)), unsafe_allow_html=True)
            question = st.text_area(translate("direct_inquiry_placeholder", lang), key="direct_q")
            if st.button(translate("direct_consult_btn", lang), type="primary", use_container_width=True):
                asyncio.run(process_consultation(question))
                st.rerun()
            st.markdown(card_end(), unsafe_allow_html=True)

    if st.session_state.last_reading_id and st.session_state.messages:
        with st.expander(translate("rate_reading", lang), expanded=True):
            st.write(translate("relevant_q", lang))
            yes, no = st.columns(2)
            if yes.button(translate("yes", lang), use_container_width=True):
                process_feedback(st.session_state.user_id, st.session_state.last_hex_num, True, 3)
                st.success(translate("feedback_success", lang))
                st.session_state.last_reading_id = None
            if no.button(translate("not_really", lang), use_container_width=True):
                process_feedback(st.session_state.user_id, st.session_state.last_hex_num, False, 1)
                st.success(translate("feedback_success", lang))
                st.session_state.last_reading_id = None

    if st.session_state.messages and st.session_state.get("suggestion_chips"):
        st.markdown("##### 💡 Suggested Questions")
        chip_cols = st.columns(len(st.session_state.suggestion_chips))
        for idx, chip_text in enumerate(st.session_state.suggestion_chips):
            with chip_cols[idx]:
                if st.button(chip_text, key=f"chip_btn_{idx}", use_container_width=True):
                    asyncio.run(process_consultation(chip_text))
                    st.rerun()

    input_placeholder = "Ask a question or continue your consultation..."
    if st.session_state.get("active_reading"):
        p_name = st.session_state.active_reading["primary_hex"]["name_en"]
        p_num = st.session_state.active_reading["primary_hex"]["number"]
        input_placeholder = f"Ask how Hexagram #{p_num} ({p_name}) applies to your situation..."

    if prompt := st.chat_input(input_placeholder):
        asyncio.run(process_consultation(prompt))
        st.rerun()

elif menu == translate("nav_history", lang):
    st.title(translate("history_title", lang))
    history = get_reading_history(st.session_state.user_id)
    if not history:
        st.info(translate("no_history", lang))
    else:
        for entry in history:
            date = datetime.datetime.fromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
            with st.expander(translate("history_expander", lang).format(date=date, num=entry.get("hexagram_number"))):
                st.markdown(entry.get("oracle_response", ""))

elif menu == translate("nav_examples", lang):
    st.title(translate("nav_examples", lang))
    st.markdown(card_begin(translate("nav_examples", lang)), unsafe_allow_html=True)
    st.write(translate("examples_desc", lang))
    for _, data in list(HEXAGRAM_PROFILES.items())[:10]:
        st.markdown(f"**#{data['number']} {data['name_en']} ({data['name_zh']})**: {data['short_meaning']}")
    st.markdown(card_end(), unsafe_allow_html=True)

elif menu == translate("nav_how", lang):
    st.title(translate("nav_how", lang))
    guide_map = {"en": "USER_GUIDE.md", "id": "USER_GUIDE_KIDS_ID.md", "zh": "USER_GUIDE_KIDS_ZH.md"}
    try:
        with open(guide_map.get(lang, "USER_GUIDE.md"), "r", encoding="utf-8") as guide:
            st.markdown(guide.read())
    except OSError:
        st.error("Guide not found.")

elif menu == translate("nav_settings", lang):
    st.title(translate("nav_settings", lang))
    st.write(f"{translate('user_id_label', lang)}: `{st.session_state.user_id}`")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.active_reading = None
        st.session_state.suggestion_chips = []
        st.rerun()
