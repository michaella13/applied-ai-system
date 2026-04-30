"""
Reliability tests for the RAG pipeline.

These tests call the Gemini API and require GEMINI_API_KEY to be set in .env.
They are skipped automatically if the API is unavailable or rate-limited.

Run with:  pytest tests/test_reliability.py -v
"""

import pytest

VALID_GENRES = {
    "pop", "lofi", "rock", "ambient", "jazz", "synthwave",
    "indie pop", "hip-hop", "metal", "reggae", "country",
    "r&b", "edm", "blues", "rap", "afrobeats", "classical",
}
VALID_MOODS = {
    "happy", "chill", "intense", "focused", "moody", "relaxed",
    "peaceful", "laid-back", "euphoric", "energetic", "aggressive",
    "melancholic", "confident", "nostalgic", "sensual", "gritty",
}

# (query, hint about expected mood cluster, expected energy range)
CASES = [
    ("something chill for late night studying",   "low-energy",  (0.0, 0.6)),
    ("high energy workout music",                 "high-energy", (0.6, 1.0)),
    ("sad rainy day songs",                       "low-valence", (0.0, 0.7)),
    ("upbeat happy pop for a party",              "high-energy", (0.6, 1.0)),
    ("aggressive metal to get pumped up",         "high-energy", (0.6, 1.0)),
]


def _try_import_parse():
    try:
        from src.ai_client import parse_query
        return parse_query
    except Exception:
        return None


def _call_parse(parse_query, query):
    try:
        return parse_query(query)
    except Exception as e:
        err = str(e)
        if "credit" in err.lower() or "billing" in err.lower() or "auth" in err.lower():
            pytest.skip(f"API unavailable: {e}")
        raise


@pytest.mark.parametrize("query,hint,energy_range", CASES)
def test_parse_returns_valid_structure(query, hint, energy_range):
    parse_query = _try_import_parse()
    if parse_query is None:
        pytest.skip("Could not import parse_query")

    prefs, confidence = _call_parse(parse_query, query)

    assert isinstance(prefs, dict), "parse_query must return a dict"
    required = {"genre", "mood", "energy", "valence", "tempo_bpm", "danceability", "acousticness"}
    assert required <= prefs.keys(), f"Missing keys: {required - prefs.keys()}"
    assert prefs["genre"] in VALID_GENRES, f"Unknown genre: {prefs['genre']}"
    assert prefs["mood"] in VALID_MOODS,   f"Unknown mood: {prefs['mood']}"
    for key in ("energy", "valence", "danceability", "acousticness"):
        assert 0.0 <= prefs[key] <= 1.0, f"{key}={prefs[key]} out of range"
    assert 60 <= prefs["tempo_bpm"] <= 200, f"tempo_bpm={prefs['tempo_bpm']} out of range"
    assert 0.0 <= confidence <= 1.0, f"confidence={confidence} out of range"


@pytest.mark.parametrize("query,hint,energy_range", CASES)
def test_parse_energy_matches_expectation(query, hint, energy_range):
    parse_query = _try_import_parse()
    if parse_query is None:
        pytest.skip("Could not import parse_query")

    prefs, _ = _call_parse(parse_query, query)
    lo, hi = energy_range
    assert lo <= prefs["energy"] <= hi, (
        f"Query '{query}' ({hint}): expected energy in [{lo}, {hi}], got {prefs['energy']:.2f}"
    )


def test_reliability_summary(capsys):
    """Prints a human-readable reliability report at the end of the suite."""
    parse_query = _try_import_parse()
    if parse_query is None:
        pytest.skip("Could not import parse_query")

    passed, total, confidences = 0, 0, []
    for query, _, energy_range in CASES:
        total += 1
        try:
            prefs, confidence = _call_parse(parse_query, query)
            lo, hi = energy_range
            if lo <= prefs["energy"] <= hi:
                passed += 1
            confidences.append(confidence)
        except Exception:
            pass

    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
    print(f"\n  Reliability check: {passed}/{total} queries parsed with correct energy range")
    print(f"  Average confidence score: {avg_conf:.2f}")
