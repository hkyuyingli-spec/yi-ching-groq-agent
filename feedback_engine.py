from typing import Dict, Any
from firebase_config import get_user_profile, update_user_profile_weights

def process_feedback(user_id: str, hexagram_number: int, relevant: bool, clarity_stars: int):
    """
    Update user profile weights based on feedback.
    Logic:
    If relevant = true:
    1 star: +0.1
    2 stars: +0.2
    3 stars: +0.4
    If relevant = false: -0.3
    Weight limits: min = 0.1, max = 2.0
    """
    profile = get_user_profile(user_id)
    weights = profile.get("hexagram_weights", {})
    
    hex_key = str(hexagram_number)
    current_weight = weights.get(hex_key, 1.0)
    
    if relevant:
        if clarity_stars == 1:
            current_weight += 0.1
        elif clarity_stars == 2:
            current_weight += 0.2
        elif clarity_stars == 3:
            current_weight += 0.4
    else:
        current_weight -= 0.3
        
    # Apply limits
    current_weight = max(0.1, min(2.0, current_weight))
    
    weights[hex_key] = round(current_weight, 2)
    update_user_profile_weights(user_id, weights)
    
    return weights
