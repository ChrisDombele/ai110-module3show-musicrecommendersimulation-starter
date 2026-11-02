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
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dicts with numeric fields converted to int/float."""
    print(f"Loading songs from {csv_path}...")

    int_fields = ("id",)
    float_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")

    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)
    return songs

# Algorithm Recipe weights (see README "How The System Works"); they sum to the max score of 5.0.
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTIC_WEIGHT = 0.5

# likes_acoustic is a yes/no flag, so it maps to a target acousticness.
ACOUSTIC_TARGET_LIKED = 0.8
ACOUSTIC_TARGET_DISLIKED = 0.2

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song (max 5.0) against a taste profile and return (score, list of reasons)."""
    score = 0.0
    reasons: List[str] = []

    if song["genre"] == user_prefs["favorite_genre"]:
        score += GENRE_WEIGHT
        reasons.append(f"genre match: {song['genre']} (+{GENRE_WEIGHT:.2f})")

    if song["mood"] == user_prefs["favorite_mood"]:
        score += MOOD_WEIGHT
        reasons.append(f"mood match: {song['mood']} (+{MOOD_WEIGHT:.2f})")

    energy_points = ENERGY_WEIGHT * (1 - abs(song["energy"] - user_prefs["target_energy"]))
    score += energy_points
    reasons.append(
        f"energy closeness: {song['energy']:.2f} vs target {user_prefs['target_energy']:.2f} (+{energy_points:.2f})"
    )

    acoustic_target = ACOUSTIC_TARGET_LIKED if user_prefs["likes_acoustic"] else ACOUSTIC_TARGET_DISLIKED
    acoustic_points = ACOUSTIC_WEIGHT * (1 - abs(song["acousticness"] - acoustic_target))
    score += acoustic_points
    reasons.append(
        f"acousticness closeness: {song['acousticness']:.2f} vs target {acoustic_target:.2f} (+{acoustic_points:.2f})"
    )

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song with score_song and return the top k as (song, score, explanation), best first."""
    # Judge every song in the catalog first, so each one has a numeric score.
    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))

    # Then sort the whole list, highest score first, and keep the top k.
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
