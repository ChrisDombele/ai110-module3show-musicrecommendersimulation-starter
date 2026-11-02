"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


# Taste profiles. Categorical keys are matched exactly; numeric targets are scored by
# closeness (1 - |song value - target|). Valence, danceability and tempo targets are
# stored for later experiments but are not scored in the base recipe.
PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.85,
        "likes_acoustic": False,       # treated as target acousticness of ~0.2
        "target_valence": 0.85,
        "target_danceability": 0.85,
        "target_tempo": 125,           # BPM
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.40,
        "likes_acoustic": True,        # treated as target acousticness of ~0.8
        "target_valence": 0.60,
        "target_danceability": 0.60,
        "target_tempo": 80,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.92,
        "likes_acoustic": False,
        "target_valence": 0.45,
        "target_danceability": 0.65,
        "target_tempo": 150,
    },
}


def main() -> None:
    songs = load_songs("data/songs.csv")
    for s in songs:
        print(f"{s['id']:>2}. {s['title']} - {s['artist']} ({s['genre']}/{s['mood']})")

    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print(f"\n=== Top recommendations for {name} ===\n")
        for rec in recommendations:
            # Each item is (song, score, explanation)
            song, score, explanation = rec
            print(f"{song['title']} - Score: {score:.2f}")
            print(f"Because: {explanation}")
            print()


if __name__ == "__main__":
    main()
