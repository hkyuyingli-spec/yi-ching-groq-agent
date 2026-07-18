from unittest.mock import patch

from core.iching_core import IChingCore
from hexagram_profiles import HEXAGRAM_PROFILES


def test_cast_preserves_line_order_and_changes_old_lines():
    core = IChingCore()
    throws = iter([
        (7, "young yang", "yang", False),
        (8, "young yin", "yin", False),
        (6, "old yin", "yin", True),
        (9, "old yang", "yang", True),
        (7, "young yang", "yang", False),
        (8, "young yin", "yin", False),
    ])
    core.throw_coins = lambda: next(throws)

    cast = core.cast_hexagram()

    assert cast["primary_bits"] == "100110"
    assert cast["primary"] == HEXAGRAM_PROFILES["100110"]["number"]
    assert cast["changing_lines"] == [3, 4]
    assert cast["transformed_bits"] == "101010"
    assert cast["transformed"] == HEXAGRAM_PROFILES["101010"]["number"]


def test_each_coin_total_has_the_correct_line_semantics():
    core = IChingCore()
    expected = {
        6: ("old yin", "yin", True),
        7: ("young yang", "yang", False),
        8: ("young yin", "yin", False),
        9: ("old yang", "yang", True),
    }
    coin_sequences = {
        6: [2, 2, 2],
        7: [2, 2, 3],
        8: [2, 3, 3],
        9: [3, 3, 3],
    }
    for total, sequence in coin_sequences.items():
        with patch("core.iching_core.random.choice", side_effect=sequence):
            value, line_type, polarity, changing = core.throw_coins()
        assert value == total
        assert (line_type, polarity, changing) == expected[total]
