import streamlit as st

def apply_zen_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

        /* Main Background and Body Text - Default to Inter for UI */
        .stApp {
            background-color: #FDFBF7;
            color: #222222;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* UI Labels, Buttons, Navigation */
        .stButton>button, .stSelectbox, .stRadio, [data-baseweb="tab-list"], .stMetric {
            font-family: 'Inter', sans-serif !important;
        }

        /* Headers - Wisdom/Titles use Lora */
        h1, h2, h3 {
            color: #4A3728 !important;
            font-family: 'Lora', serif;
            font-weight: 600;
        }

        /* Professional Cards */
        .pro-card {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #E8E4D9;
        }

        /* Oracle Response & Wisdom Text - Explicitly Lora */
        .oracle-response, .wisdom-text, .interpretation {
            font-family: 'Lora', serif !important;
            line-height: 1.8;
            font-size: 1.1rem;
            color: #333333;
        }

        .oracle-response {
            border-left: 4px solid #D4AF37;
            padding: 20px;
            background-color: #FCF9F2;
            border-radius: 0 8px 8px 0;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }

        
        /* Buttons */
        .stButton>button {
            border: 1px solid #4A3728;
            background-color: #4A3728;
            color: #FDFBF7 !important;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            background-color: #5E4A3A;
            border-color: #5E4A3A;
            box-shadow: 0 4px 12px rgba(74, 55, 40, 0.2);
        }
        
        /* Metrics and Progress */
        [data-testid="stMetricValue"] {
            color: #4A3728 !important;
            font-weight: 700;
        }
        .stProgress > div > div > div > div {
            background-color: #4A3728;
        }
        
        /* Mobile Optimizations */
        @media (max-width: 768px) {
            .pro-card {
                padding: 16px;
            }
            .oracle-response {
                padding: 15px;
                font-size: 1rem;
            }
        }
        
        /* Custom Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre;
            font-weight: 600;
            color: #666666;
        }
        .stTabs [aria-selected="true"] {
            color: #4A3728 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def card_begin(title=None):
    if title:
        return f'<div class="pro-card"><h3>{title}</h3>'
    return '<div class="pro-card">'

def card_end():
    return '</div>'

def get_element_icon(element_name):
    icons = {
        "Wood (木)": "🌿",
        "Fire (火)": "🔥",
        "Earth (土)": "🌍",
        "Metal (金)": "⚔️",
        "Water (水)": "🌊"
    }
    for key, icon in icons.items():
        if key in element_name:
            return icon
    return "✨"
