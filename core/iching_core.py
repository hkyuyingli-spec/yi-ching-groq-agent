import random
import json
from typing import Dict

class IChingCore:
    def __init__(self):
        self.hexagrams = self._load_hexagrams()
    
    def _load_hexagrams(self) -> Dict:
        try:
            with open('data/hexagrams.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️ hexagrams.json not found yet!")
            return {}
    
    def throw_coins(self):
        """Simulate throwing 3 coins"""
        coins = [random.choice([2, 3]) for _ in range(3)]
        total = sum(coins)
        
        if total == 6:
            return 6, "old yin", "⚋"
        elif total == 7:
            return 7, "young yang", "⚊"
        elif total == 8:
            return 8, "young yin", "⚋"
        elif total == 9:
            return 9, "old yang", "⚊"
    
    def cast_hexagram(self):
        """Cast a full hexagram (6 lines)"""
        lines = []
        line_details = []
        
        for i in range(6):  # Bottom to top
            value, line_type, symbol = self.throw_coins()
            lines.append(value)
            line_details.append({
                "position": i + 1,
                "value": value,
                "type": line_type,
                "symbol": symbol
            })
        
        # Primary Hexagram
        binary = ''.join(['1' if v in [7,9] else '0' for v in lines[::-1]])
        primary_num = int(binary, 2) + 1
        
        # Changing lines
        changing_lines = [ld for ld in line_details if "old" in ld["type"]]
        
        # Transformed Hexagram
        transformed_lines = lines.copy()
        for i, ld in enumerate(line_details):
            if ld["type"] == "old yin":
                transformed_lines[i] = 7
            elif ld["type"] == "old yang":
                transformed_lines[i] = 8
        
        trans_binary = ''.join(['1' if v in [7,9] else '0' for v in transformed_lines[::-1]])
        transformed_num = int(trans_binary, 2) + 1 if changing_lines else None
        
        return {
            "primary": primary_num,
            "transformed": transformed_num,
            "lines": line_details,
            "changing_lines": [ld["position"] for ld in changing_lines]
        }