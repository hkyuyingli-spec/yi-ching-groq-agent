from utils.translations import TRANSLATIONS
from enigma_engine import select_hexagram, encode_state_to_bits
from hexagram_profiles import HEXAGRAM_PROFILES
import datetime

def run_exhaustive_test():
    languages = ["en", "zh", "id"]
    test_states = [
        {"energy": 5, "clarity": 5, "emotional": 5, "social": 5, "direction": 5, "foundation": True},  # Peak
        {"energy": 1, "clarity": 1, "emotional": 1, "social": 1, "direction": 1, "foundation": False}, # Low
        {"energy": 3, "clarity": 3, "emotional": 3, "social": 3, "direction": 3, "foundation": True}   # Changing
    ]
    
    lang_map = {
        "en": "Please respond in English.",
        "id": "Tolong jawab dalam Bahasa Indonesia.",
        "zh": "請用繁體中文回答。"
    }
    
    results = []
    
    for lang in languages:
        t = TRANSLATIONS[lang]
        lang_instruction = lang_map[lang]
        
        for i, state in enumerate(test_states):
            # 1. Verify UI String Retrieval
            ui_check = t["title"] is not None and t["consult_btn"] is not None
            
            # 2. Select Hexagram
            user_profile = {"hexagram_weights": {}}
            history = []
            context = {"time": datetime.datetime.now().timestamp(), "streak": 0}
            selected_bits = select_hexagram(state, user_profile, history, context)
            hex_data = HEXAGRAM_PROFILES[selected_bits]
            
            # 3. Verify AI Instruction
            ai_check = lang_instruction is not None
            
            results.append({
                "lang": lang,
                "test_num": i + 1,
                "state": state,
                "hex_name": hex_data["name_en"],
                "ui_status": "OK" if ui_check else "FAIL",
                "ai_instr": lang_instruction
            })
            
    # Print Detailed Report
    print(f"{'LANG':<6} | {'TEST':<4} | {'HEXAGRAM':<20} | {'UI':<4} | {'AI INSTRUCTION'}")
    print("-" * 80)
    for res in results:
        print(f"{res['lang']:<6} | {res['test_num']:<4} | {res['hex_name']:<20} | {res['ui_status']:<4} | {res['ai_instr']}")

if __name__ == "__main__":
    run_exhaustive_test()
