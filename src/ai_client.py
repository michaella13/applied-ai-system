import json
import os
from typing import Dict, List, Tuple

from google import genai
from dotenv import load_dotenv

load_dotenv()

REQUIRED_KEYS = {"genre", "mood", "energy", "valence", "tempo_bpm", "danceability", "acousticness"}
NUMERIC_KEYS  = {"energy", "valence", "danceability", "acousticness"}
MODEL = "gemini-2.5-flash"
_client_instance: genai.Client | None = None


def _client() -> genai.Client:
    global _client_instance
    if _client_instance is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        _client_instance = genai.Client(api_key=api_key)
    return _client_instance


def parse_query(query: str) -> Tuple[Dict, float]:
    """Call #1 — convert natural language query to structured user_prefs dict.

    Returns (prefs, confidence) where confidence is 0.0–1.0.
    """
    prompt = (
        "You are a music preference parser. "
        "Given a natural language description of what someone wants to hear, "
        "return ONLY a JSON object with these exact keys:\n"
        '  "genre"        — one of: pop, lofi, rock, ambient, jazz, synthwave, '
        "indie pop, hip-hop, metal, reggae, country, r&b, edm, blues, rap, afrobeats\n"
        '  "mood"         — one of: happy, chill, intense, focused, moody, relaxed, '
        "peaceful, laid-back, euphoric, energetic, aggressive, melancholic, confident, "
        "nostalgic, sensual, gritty\n"
        '  "energy"       — float between 0.0 and 1.0\n'
        '  "valence"      — float between 0.0 and 1.0 (0=negative, 1=positive)\n'
        '  "tempo_bpm"    — float between 60 and 200\n'
        '  "danceability" — float between 0.0 and 1.0\n'
        '  "acousticness" — float between 0.0 and 1.0\n'
        '  "confidence"   — float between 0.0 and 1.0 indicating how clearly the '
        "request maps to the available genres and moods\n"
        "Return only the JSON object. No explanation, no markdown.\n\n"
        f"User request: {query}"
    )

    response = _client().models.generate_content(model=MODEL, contents=prompt)
    raw = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        prefs = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {raw}") from e

    confidence = float(prefs.pop("confidence", 1.0))

    missing = REQUIRED_KEYS - prefs.keys()
    if missing:
        raise ValueError(f"Gemini response missing keys: {missing}")

    for key in NUMERIC_KEYS:
        val = prefs[key]
        if not (0.0 <= float(val) <= 1.0):
            raise ValueError(f"'{key}' value {val} is out of range [0.0, 1.0]")

    return prefs, confidence


def generate_explanation(query: str, songs: List[Tuple[Dict, float, List[str]]]) -> str:
    """Call #2 — inject retrieved songs as context and generate a natural language explanation."""
    songs_context = "\n".join(
        f"{i+1}. \"{s['title']}\" by {s['artist']} "
        f"(genre: {s['genre']}, mood: {s['mood']}, score: {score:.2f})\n"
        f"   Reasons: {', '.join(reasons)}"
        for i, (s, score, reasons) in enumerate(songs)
    )

    prompt = (
        "You are a music recommendation assistant. "
        "You will be given a user's request and a list of songs retrieved by a scoring system. "
        "Explain why each song is a good match in a friendly, concise way. "
        "Reference the specific features (mood, energy, tempo, genre) that made each song score well. "
        "Keep your total response under 200 words.\n\n"
        f"The user asked for: \"{query}\"\n\n"
        f"The top retrieved songs are:\n{songs_context}\n\n"
        "Explain why these songs fit what the user is looking for."
    )

    response = _client().models.generate_content(model=MODEL, contents=prompt)
    return response.text.strip()
