import json
from enigma_engine import encode_state_to_bits, select_hexagram, compute_changing_lines
from feedback_engine import process_feedback
from hexagram_profiles import HEXAGRAM_PROFILES
import datetime

def run_test_scenario(scenario_name, state, user_profile, history):
    print(f"\n{'='*60}")
    print(f"SCENARIO: {scenario_name}")
    print(f"Input State: {state}")
    
    # 1. Encode bits
    bits = encode_state_to_bits(state)
    print(f"Encoded Bits: {bits}")
    
    # 2. Select Hexagram
    context = {"time": datetime.datetime.now().timestamp(), "streak": 0}
    selected_bits = select_hexagram(state, user_profile, history, context)
    hex_data = HEXAGRAM_PROFILES[selected_bits]
    print(f"Selected Hexagram: #{hex_data['number']} {hex_data['name_en']} ({hex_data['name_zh']})")
    print(f"Theme: {hex_data['theme']} | Action: {hex_data['action_type']}")
    
    # 3. Compute Changing Lines
    next_bits = compute_changing_lines(state)
    if next_bits:
        next_hex = HEXAGRAM_PROFILES[next_bits]
        print(f"Changing Lines detected! Next Hexagram: #{next_hex['number']} {next_hex['name_en']}")
    else:
        print("No changing lines.")
        
    return hex_data['number']

# Initial Setup
user_id = "test_user_123"
user_profile = {"hexagram_weights": {}}
history = []

# --- TEST 1: High Energy, High Focus ---
state1 = {
    "energy": 5,
    "clarity": 5,
    "emotional": 4,
    "social": 4,
    "direction": 5,
    "foundation": True
}
hex_num1 = run_test_scenario("Test 1 - High Energy/Focus", state1, user_profile, history)

# Simulate Feedback for Test 1
print("\n--- Processing Feedback for Test 1 ---")
print("User Rating: Relevant=True, Clarity=3 stars")
new_weights = process_feedback(user_id, hex_num1, True, 3)
print(f"Updated Weight for Hexagram #{hex_num1}: {new_weights.get(str(hex_num1))}")


# --- TEST 2: Low Energy, Reflective ---
state2 = {
    "energy": 1,
    "clarity": 2,
    "emotional": 2,
    "social": 1,
    "direction": 2,
    "foundation": False
}
hex_num2 = run_test_scenario("Test 2 - Low Energy/Reflective", state2, user_profile, history)

# Simulate Feedback for Test 2
print("\n--- Processing Feedback for Test 2 ---")
print("User Rating: Relevant=False")
new_weights = process_feedback(user_id, hex_num2, False, 1)
print(f"Updated Weight for Hexagram #{hex_num2}: {new_weights.get(str(hex_num2))}")


# --- TEST 3: Neutral State (Trigger Changing Lines) ---
# Any slider at 3 triggers a changing line
state3 = {
    "energy": 3,
    "clarity": 3,
    "emotional": 4,
    "social": 2,
    "direction": 3,
    "foundation": True
}
hex_num3 = run_test_scenario("Test 3 - Neutral (Changing Lines)", state3, user_profile, history)

print(f"\n{'='*60}")
print("DEMONSTRATION COMPLETE")
