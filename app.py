import streamlit as st
import time
import sys
import os
from dotenv import load_dotenv

# Fix for import path issues
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from core.iching_core import IChingCore
from core.interpreter import IChingInterpreter

# Page Configuration
st.set_page_config(page_title="Yi Ching AI", page_icon="☰", layout="centered")

st.title("☰ 易經 • 易経 • 주역 • إي تشينغ")
st.header(":blue[Grand Master] :orange[Yi Ching] :red[Oracle]")
st.markdown("### :green[3000 Years] of :gray[Ancient Wisdom] • :blue[Metaphysical Synthesis]")

# Initialize session state
if "core" not in st.session_state:
    st.session_state.core = IChingCore()
if "interpreter" not in st.session_state:
    st.session_state.interpreter = IChingInterpreter()

# Tab Selection for Consultation Mode
tab1, tab2 = st.tabs([":blue[🔮 I Ching Ritual (Coins)]", ":green[📜 Direct Metaphysical Consultation]"])

with tab1:
    st.markdown("#### :blue[Traditional 3-Coin Method]")
    question_iching = st.text_area(
        "What guidance do you seek from the coins?", 
        placeholder="Enter your question for the I Ching...",
        key="iching_q"
    )

    if st.button("Cast the Hexagram", type="primary", use_container_width=True):
        if not question_iching.strip():
            st.warning("⚠️ Please enter your question first.")
        else:
            with st.spinner("Casting the ancient coins..."):
                cast_result = st.session_state.core.cast_hexagram()
                time.sleep(1.2)
                
                st.success("✅ The coins have spoken!")
                
                # Display Hexagrams
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"**Primary Hexagram**")
                    st.markdown(f"### :blue[#{cast_result['primary']}]")
                
                with col2:
                    if cast_result.get('transformed'):
                        st.subheader(f"**Transformed Hexagram**")
                        st.markdown(f"### :orange[#{cast_result['transformed']}]")
                
                # Get hexagram data
                primary_hex = st.session_state.core.hexagrams.get(str(cast_result['primary']), {})
                transformed_hex = None
                if cast_result.get('transformed'):
                    transformed_hex = st.session_state.core.hexagrams.get(str(cast_result['transformed']), {})
                
                # Get AI Interpretation
                with st.spinner("Consulting the Oracle..."):
                    reading = st.session_state.interpreter.get_reading(
                        question=question_iching,
                        primary_hex=primary_hex,
                        transformed_hex=transformed_hex,
                        changing_lines=cast_result['changing_lines'],
                        primary_num=cast_result['primary'],
                        transformed_num=cast_result.get('transformed')
                    )
                
                st.markdown("### 🌀 Master's Guidance")
                st.write(reading)

with tab2:
    st.markdown("#### :green[Direct Expert Advice]")
    st.write("Ask directly about Feng Shui, Health (TCM), Life Path, or Prosperity without casting coins.")
    question_direct = st.text_area(
        "What is your metaphysical inquiry?", 
        placeholder="e.g. How can I improve the Feng Shui of my office? What are the TCM principles for better sleep?",
        key="direct_q"
    )

    if st.button("Consult the Master", type="primary", use_container_width=True):
        if not question_direct.strip():
            st.warning("⚠️ Please enter your question first.")
        else:
            with st.spinner("Analyzing the Flow of Qi..."):
                reading = st.session_state.interpreter.get_direct_reading(question_direct)
                
                st.markdown("### 📜 Master's Direct Consultation")
                st.write(reading)

# Sidebar
with st.sidebar:
    st.header("📜 :gray[Consultation Menu]")
    
    with st.expander(":blue[🔮 I Ching & Life Path (Water)]", expanded=True):
        st.write("""
        **Best for:** Decisions, relationships, and spiritual growth.
        *Example:* "How can I resolve the tension in my team?" or "Should I embark on this new venture?"
        """)

    with st.expander(":orange[🏠 Feng Shui & Space (Earth)]"):
        st.write("""
        **Best for:** Home/Office energy, Xuan Kong, and Environmental flow.
        *Example:* "How to optimize my south-facing office for Period 9?" or "My bedroom feels stagnant, how to improve the Qi?"
        """)

    with st.expander(":green[🍃 Health & TCM (Wood)]"):
        st.write("""
        **Best for:** Vitality, seasonal wellness, and energetic balance.
        *Example:* "What TCM principles support better sleep?" or "How to maintain my Lung Qi during autumn?"
        """)

    with st.expander(":red[💰 Prosperity & Timing (Fire)]"):
        st.write("""
        **Best for:** Business timing, investments, and Period 9 transitions.
        *Example:* "What industries are favored in Period 9?" or "Is this a auspicious time for expansion?"
        """)
    
    st.divider()
    st.write("**:gray[The Five Elements Color Key]**")
    st.markdown("""
    - :blue[Water]: Wisdom & Career
    - :green[Wood]: Health & Growth
    - :red[Fire]: Prosperity & Success
    - :orange[Earth]: Stability & Space
    - :gray[Metal]: Refinement & Vitality
    """)
    
    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()
