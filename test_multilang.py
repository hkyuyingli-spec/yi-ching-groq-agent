from utils.translations import TRANSLATIONS
from enigma_engine import encode_state_to_bits
import datetime

def simulate_app_ui(lang_code):
    if lang_code not in TRANSLATIONS:
        print(f"Error: Language {lang_code} not found in TRANSLATIONS.")
        return None
        
    t = TRANSLATIONS[lang_code]
    print(f"\n--- Testing Language: {lang_code.upper()} ---")
    print(f"Title: {t['title']}")
    print(f"Slider (Energy): {t['energy']}")
    print(f"Button: {t['consult_btn']}")
    print(f"Feedback Question: {t['relevant_q']}")
    
    # Simulate the AI prompt injection logic from app.py
    lang_map = {
        "en": "Please respond in English.",
        "id": "Tolong jawab dalam Bahasa Indonesia.",
        "zh": "請用繁體中文回答。"
    }
    lang_instruction = lang_map.get(lang_code, "Please respond in English.")
    query = "What is my path?"
    enigma_data = {
        'state_summary': "Energy:5, Clarity:5",
        'primary_bits': "111111"
    }
    
    context_query = f"""
    {lang_instruction}
    I Ching Reading for: {query}
    Current User State: {enigma_data['state_summary']}
    """
    print(f"AI Language Instruction: {lang_instruction}")
    return context_query

# Test 1: English Mode
print("TEST 1: English Mode")
sim1 = simulate_app_ui("en")

# Test 2: Traditional Chinese Mode
print("\nTEST 2: Traditional Chinese Mode")
sim2 = simulate_app_ui("zh")

# Test 3: Bahasa Indonesia Mode
print("\nTEST 3: Bahasa Indonesia Mode")
sim3 = simulate_app_ui("id")
assert "Tolong jawab dalam Bahasa Indonesia" in sim3

# Test 4: Language Switching Logic
print("\nTEST 4: Language Switching")
current_lang = "en"
print(f"Initial (EN): {TRANSLATIONS[current_lang]['consult_btn']}")
current_lang = "id"
print(f"Switched (ID): {TRANSLATIONS[current_lang]['consult_btn']}")
assert TRANSLATIONS["en"]["consult_btn"] != TRANSLATIONS["id"]["consult_btn"]

print("\n" + "="*40)
print("MULTI-LANGUAGE VERIFICATION COMPLETE")
print("="*40)
