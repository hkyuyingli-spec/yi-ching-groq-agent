import streamlit as st

def apply_zen_styles():
    st.markdown("""
        <style>
        /* Main Background and Text */
        .stApp {
            background-color: #0E1117;
            color: #E0E0E0;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #D4AF37 !important;
            font-family: 'Georgia', serif;
        }
        
        /* Sidebar Glassmorphism */
        section[data-testid="stSidebar"] {
            background-color: rgba(30, 34, 45, 0.7);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(212, 175, 55, 0.2);
        }
        
        /* Chat Message Styling */
        [data-testid="stChatMessage"] {
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 20px;
            margin-bottom: 10px;
        }
        
        /* Oracle Response Container */
        .oracle-response {
            border-left: 3px solid #D4AF37;
            padding-left: 20px;
            background-color: rgba(212, 175, 55, 0.03);
            font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
            line-height: 1.6;
        }
        
        /* Progress Bar Styling */
        .stProgress > div > div > div > div {
            background-color: #D4AF37;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #D4AF37 !important;
        }
        
        /* Buttons */
        .stButton>button {
            border: 1px solid #D4AF37;
            background-color: transparent;
            color: #D4AF37;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #D4AF37;
            color: #0E1117;
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.4);
        }
        
        /* Ritual Line Animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .ritual-line {
            animation: fadeIn 1s ease-out forwards;
            color: #D4AF37;
            font-size: 1.2rem;
            margin: 5px 0;
        }
        </style>
    """, unsafe_allow_html=True)

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
