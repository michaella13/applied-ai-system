import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        prefs = {
            "genre":        user.favorite_genre,
            "mood":         user.favorite_mood,
            "energy":       user.target_energy,
            "valence":      0.7,
            "tempo_bpm":    120.0,
            "danceability": 0.7,
            "acousticness": 0.8 if user.likes_acoustic else 0.2,
        }
        song_dicts = [s.__dict__ for s in self.songs]
        scored = sorted(
            [(s, *score_song(prefs, d)) for s, d in zip(self.songs, song_dicts)],
            key=lambda x: x[1],
            reverse=True,
        )
        return [s for s, _, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        from src.ai_client import generate_explanation
        query = (
            f"A {user.favorite_mood} {user.favorite_genre} fan "
            f"with {'high' if user.target_energy > 0.6 else 'low'} energy preference"
        )
        prefs = {
            "genre":        user.favorite_genre,
            "mood":         user.favorite_mood,
            "energy":       user.target_energy,
            "valence":      0.7,
            "tempo_bpm":    120.0,
            "danceability": 0.7,
            "acousticness": 0.8 if user.likes_acoustic else 0.2,
        }
        score, reasons = score_song(prefs, song.__dict__)
        return generate_explanation(query, [(song.__dict__, score, reasons)])

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    print(f"Loaded songs: {len(songs)}")
    return songs

# Mood clusters for partial credit. Moods absent from all clusters (e.g. "gritty",
# "nostalgic") score 0 unless they are an exact match.
MOOD_CLUSTERS = [
    {"chill", "relaxed", "peaceful", "laid-back"},
    {"happy", "euphoric", "energetic"},
    {"intense", "aggressive"},
    {"moody", "melancholic"},
    {"focused", "confident"},
]

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    user_prefs keys: mood, genre, energy, valence, tempo_bpm, danceability, acousticness
    Returns: (total_score, reasons)  — max possible score is 15.5 pts
    """
    score = 0.0
    reasons = []

    # Mood: 5 pts exact, 2.5 pts same cluster
    user_mood = user_prefs["mood"]
    song_mood = song["mood"]
    if user_mood == song_mood:
        score += 5.0
        reasons.append("mood match (+5.0)")
    else:
        for cluster in MOOD_CLUSTERS:
            if user_mood in cluster and song_mood in cluster:
                score += 2.5
                reasons.append(f"similar mood — {song_mood} ≈ {user_mood} (+2.5)")
                break

    # Genre: 3 pts exact
    if user_prefs["genre"] == song["genre"]:
        score += 3.0
        reasons.append("genre match (+3.0)")

    # Continuous features: weight × (1 - |reference - candidate| / scale)
    # tempo_bpm is divided by 200 to normalise its BPM range to [0, 1].
    continuous = [
        ("energy",       3.0, user_prefs["energy"],       song["energy"],       1.0),
        ("valence",      2.0, user_prefs["valence"],       song["valence"],      1.0),
        ("tempo_bpm",    1.0, user_prefs["tempo_bpm"],     song["tempo_bpm"],    200.0),
        ("danceability", 1.0, user_prefs["danceability"],  song["danceability"], 1.0),
        ("acousticness", 0.5, user_prefs["acousticness"],  song["acousticness"], 1.0),
    ]
    for feature, weight, ref, candidate, scale in continuous:
        pts = weight * (1 - abs(ref - candidate) / scale)
        score += pts
        reasons.append(f"{feature} (+{pts:.2f})")

    return round(score, 4), reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, List[str]]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Returns the top k songs as (song_dict, score, reasons) tuples,
    sorted from highest to lowest score.
    """
    scored = [
        (song, score, reasons)
        for song in songs
        for score, reasons in [score_song(user_prefs, song)]
    ]

    # sorted() is used instead of .sort() because scored is a fresh list built
    # from a list comprehension — sorted() returns a new sorted list without
    # modifying the original, which keeps the function free of side effects.
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
