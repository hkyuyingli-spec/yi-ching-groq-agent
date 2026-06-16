from typing import List, Dict, Any, Optional
import datetime
from hexagram_profiles import HEXAGRAM_PROFILES

def encode_state_to_bits(state: Dict[str, Any]) -> str:
    """
    Converts user state into a 6-bit hexagram profile.
    Rules: >=3 = Yang (1), <3 = Yin (0)
    Order: energy, clarity, emotional, social, direction, foundation
    """
    bits = ""
    keys = ["energy", "clarity", "emotional", "social", "direction"]
    for key in keys:
        val = state.get(key, 3)
        bits += "1" if val >= 3 else "0"
    
    # Foundation is a bool
    foundation = state.get("foundation", True)
    bits += "1" if foundation else "0"
    
    return bits

def reflector_filter(user_bit_string: str, all_hexagrams: Dict[str, Dict[str, Any]]) -> List[str]:
    """
    Eliminate incompatible hexagrams.
    Logic: Calculate bit conflicts. Allow maximum 2 conflicting bits.
    """
    candidates = []
    for hex_bits in all_hexagrams.keys():
        conflicts = sum(1 for b1, b2 in zip(user_bit_string, hex_bits) if b1 != b2)
        if conflicts <= 2:
            candidates.append(hex_bits)
    return candidates

def compute_relevance(hex_bits: str, user_profile: Dict[str, Any], history: List[Dict[str, Any]]) -> float:
    """
    Compute relevance score for a hexagram.
    Base score = 1.0
    Boost if: previously relevant, previously high clarity
    Penalise if: low relevance, repeated within last 5 readings
    """
    hex_data = HEXAGRAM_PROFILES.get(hex_bits, {})
    hex_number = str(hex_data.get("number", ""))
    
    # Base score from user_profile weights if available
    weights = user_profile.get("hexagram_weights", {})
    score = weights.get(hex_number, 1.0)
    
    # History penalties
    last_5 = history[-5:] if history else []
    for record in last_5:
        if str(record.get("hexagram_number")) == hex_number:
            score *= 0.5  # Penalize repetition
            
    return score

def apply_context_weights(candidates: List[str], context: Dict[str, Any]) -> Dict[str, float]:
    """
    Apply small weighting adjustments based on context.
    Context inputs: time of day, streak count, weekday/weekend
    """
    weighted_candidates = {}
    time_val = context.get("time")
    if isinstance(time_val, (int, float)):
        now = datetime.datetime.fromtimestamp(time_val)
    elif isinstance(time_val, datetime.datetime):
        now = time_val
    else:
        now = datetime.datetime.now()
        
    hour = now.hour
    is_weekend = now.weekday() >= 5
    streak = context.get("streak", 0)
    
    for bits in candidates:
        hex_data = HEXAGRAM_PROFILES.get(bits, {})
        score = 1.0
        
        # Example context logic:
        # High energy hexagrams favored in the morning
        if 5 <= hour <= 11 and hex_data.get("energy_level") == "high":
            score += 0.1
        # Reflective hexagrams favored at night
        if (hour >= 20 or hour <= 4) and hex_data.get("action_type") == "reflect":
            score += 0.1
        # Connect favored on weekends
        if is_weekend and hex_data.get("action_type") == "connect":
            score += 0.1
        # Streak bonus
        if streak > 3:
            score += 0.05
            
        weighted_candidates[bits] = score
        
    return weighted_candidates

def select_hexagram(user_state: Dict[str, Any], user_profile: Dict[str, Any], history: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
    """
    Selection Pipeline:
    1. encode_state_to_bits
    2. reflector_filter
    3. compute_relevance & apply_context_weights
    4. return highest score
    """
    user_bits = encode_state_to_bits(user_state)
    candidates = reflector_filter(user_bits, HEXAGRAM_PROFILES)
    
    # If no candidates (should not happen with 2-bit tolerance), use all
    if not candidates:
        candidates = list(HEXAGRAM_PROFILES.keys())
        
    final_scores = {}
    context_weights = apply_context_weights(candidates, context)
    
    for bits in candidates:
        relevance = compute_relevance(bits, user_profile, history)
        final_scores[bits] = relevance * context_weights.get(bits, 1.0)
        
    # Return hex bits with highest score
    return max(final_scores, key=final_scores.get)

def compute_changing_lines(slider_values: Dict[str, int]) -> Optional[str]:
    """
    Rule: Slider value == 3 becomes changing line.
    Flip associated bits.
    Return next hexagram bit string.
    """
    # Assuming slider_values keys match the order in encode_state_to_bits
    # bits: energy, clarity, emotional, social, direction, foundation
    keys = ["energy", "clarity", "emotional", "social", "direction"]
    bits = []
    changing = False
    
    # We need the primary bits to flip them
    # But wait, the function should probably take the primary bits too
    # or just reconstruct them.
    
    primary_bits = []
    transformed_bits = []
    
    for key in keys:
        val = slider_values.get(key, 3)
        bit = 1 if val >= 3 else 0
        primary_bits.append(bit)
        
        if val == 3:
            transformed_bits.append(1 - bit) # Flip
            changing = True
        else:
            transformed_bits.append(bit)
            
    # Foundation (not a slider, but let's assume it doesn't change)
    foundation = slider_values.get("foundation", True)
    f_bit = 1 if foundation else 0
    primary_bits.append(f_bit)
    transformed_bits.append(f_bit)
    
    if not changing:
        return None
        
    return "".join(map(str, transformed_bits))
