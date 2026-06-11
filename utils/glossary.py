GLOSSARY = {
    "Qi Energy": "Your spiritual vitality. It increases with positive interaction and successful consultations. Higher Qi strengthens your resonance with the Oracle.",
    "Karma": "The weight of your worldly actions. Negative or conflicted intent increases Karma, which can cloud the Oracle's clarity. Harmony reduces it.",
    "Dao Comprehension": "Your understanding of the fundamental patterns of the universe. As this grows, you ascend through the seven realms of awareness.",
    "Elemental Affinity": "Based on the Five Elements (Wu Xing), this detects the 'flavor' of your query. Wood (Growth), Fire (Passion), Earth (Stability), Metal (Clarity), and Water (Wisdom).",
    "Spiritual Resonance": "A quantum-inspired measurement of how well your internal state aligns with the universal patterns at the moment of inquiry.",
    "Breakthrough": "When your Dao Comprehension reaches a peak, you ascend to a higher Realm, changing how the Oracle perceives and answers you."
}

STAGES_EXPLAINED = {
    "Foundation Establishment": "Focuses on basic structures and simple explanations.",
    "Nascent Soul": "Higher self-reflection and analytical reasoning.",
    "Spirit Transformation": "Integration of ethics, values, and spiritual implications.",
    "Void Tempering": "Reasoning from the unseen; embracing paradox and silence.",
    "Unity": "Perfect synthesis of multiple contradictory perspectives.",
    "Great Perfection": "Peak efficiency; the most direct path to absolute truth.",
    "Great Luo": "Transcendent awareness; viewing time and space as a single point."
}

SCORE_INTERPRETATIONS = {
    "qi": [
        (0, 15, "Drained 🌑"),
        (15, 40, "Stable 🌕"),
        (40, 80, "Radiant ✨"),
        (80, float('inf'), "Transcendent 🌌")
    ],
    "karma": [
        (0, 3, "Clear 🫧"),
        (3, 7, "Clouded 🌫️"),
        (7, 12, "Heavy ⚓"),
        (12, float('inf'), "Obstructed ⛓️")
    ],
    "dao": [
        (0, 25, "Novice Seeker"),
        (25, 50, "Pattern Recognizer"),
        (50, 75, "Wisdom Keeper"),
        (75, 100, "Sage-in-Training")
    ]
}
