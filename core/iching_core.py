import json
import random
from pathlib import Path
from typing import Dict

from hexagram_profiles import HEXAGRAM_PROFILES


class IChingCore:
    """Traditional three-coin I Ching casting engine.

    Lines are stored and encoded from bottom (first throw) to top (sixth
    throw), matching the bit order used by HEXAGRAM_PROFILES.
    """

    def __init__(self):
        self.hexagrams = self._load_hexagrams()

    def _load_hexagrams(self) -> Dict:
        path = Path(__file__).resolve().parent.parent / "data" / "hexagrams.json"
        try:
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def throw_coins(self):
        """Throw three fair coins and return one I Ching line.

        The totals 6, 7, 8, and 9 occur with probabilities 1/8, 3/8, 3/8,
        and 1/8 respectively. Old lines (6 and 9) are changing lines.
        """
        total = sum(random.choice([2, 3]) for _ in range(3))
        outcomes = {
            6: ("old yin", "yin", True),
            7: ("young yang", "yang", False),
            8: ("young yin", "yin", False),
            9: ("old yang", "yang", True),
        }
        line_type, polarity, changing = outcomes[total]
        return total, line_type, polarity, changing

    @staticmethod
    def _lines_to_bits(lines) -> str:
        """Encode bottom-to-top lines as the profile's six-bit key."""
        return "".join("1" if value in (7, 9) else "0" for value in lines)

    def cast_hexagram(self) -> Dict:
        """Cast six coin lines and resolve the primary and changed hexagrams."""
        lines = []
        line_details = []

        for position in range(1, 7):
            value, line_type, polarity, changing = self.throw_coins()
            lines.append(value)
            line_details.append({
                "position": position,
                "value": value,
                "type": line_type,
                "polarity": polarity,
                "changing": changing,
            })

        primary_bits = self._lines_to_bits(lines)
        changing_lines = [line["position"] for line in line_details if line["changing"]]
        transformed_lines = [
            7 if value == 6 else 8 if value == 9 else value
            for value in lines
        ]
        transformed_bits = self._lines_to_bits(transformed_lines) if changing_lines else None

        primary_profile = HEXAGRAM_PROFILES[primary_bits]
        transformed_profile = HEXAGRAM_PROFILES[transformed_bits] if transformed_bits else None
        return {
            "primary_bits": primary_bits,
            "transformed_bits": transformed_bits,
            "primary": primary_profile["number"],
            "transformed": transformed_profile["number"] if transformed_profile else None,
            "lines": line_details,
            "changing_lines": changing_lines,
        }
