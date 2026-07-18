"""Deterministic Wu Xing interpretation for a cast hexagram's trigrams."""

TRIGRAM_ELEMENTS = {
    "Heaven": "Metal",
    "Lake": "Metal",
    "Fire": "Fire",
    "Thunder": "Wood",
    "Wind": "Wood",
    "Water": "Water",
    "Mountain": "Earth",
    "Earth": "Earth",
}

ELEMENT_THEMES = {
    "Wood": "growth and initiative",
    "Fire": "passion and visibility",
    "Earth": "stability and care",
    "Metal": "clarity and discernment",
    "Water": "wisdom and caution",
}

GENERATES = {
    "Wood": "Fire",
    "Fire": "Earth",
    "Earth": "Metal",
    "Metal": "Water",
    "Water": "Wood",
}

CONTROLS = {
    "Wood": "Earth",
    "Earth": "Water",
    "Water": "Fire",
    "Fire": "Metal",
    "Metal": "Wood",
}


def describe_hexagram_feng_shui(profile: dict) -> dict:
    """Return the elements, relationship, and user-facing trigram summary."""
    upper_trigram = profile["trigram_upper"]
    lower_trigram = profile["trigram_lower"]
    upper_element = TRIGRAM_ELEMENTS[upper_trigram]
    lower_element = TRIGRAM_ELEMENTS[lower_trigram]

    if upper_element == lower_element:
        relationship = "harmonious"
        description = f"a shared focus on {ELEMENT_THEMES[upper_element]}"
    elif GENERATES[upper_element] == lower_element:
        relationship = "upper_supports_lower"
        description = (
            f"support flowing from {ELEMENT_THEMES[upper_element]} "
            f"toward {ELEMENT_THEMES[lower_element]}"
        )
    elif GENERATES[lower_element] == upper_element:
        relationship = "lower_supports_upper"
        description = (
            f"support rising from {ELEMENT_THEMES[lower_element]} "
            f"toward {ELEMENT_THEMES[upper_element]}"
        )
    elif CONTROLS[upper_element] == lower_element:
        relationship = "upper_controls_lower"
        description = (
            f"a tension between {ELEMENT_THEMES[upper_element]} "
            f"and {ELEMENT_THEMES[lower_element]}"
        )
    else:
        relationship = "lower_controls_upper"
        description = (
            f"a tension between {ELEMENT_THEMES[lower_element]} "
            f"and {ELEMENT_THEMES[upper_element]}"
        )

    return {
        "upper_trigram": upper_trigram,
        "lower_trigram": lower_trigram,
        "upper_element": upper_element,
        "lower_element": lower_element,
        "relationship": relationship,
        "summary": (
            f"{upper_trigram} ({upper_element}) above, "
            f"{lower_trigram} ({lower_element}) below — {description}."
        ),
    }
