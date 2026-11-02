"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    for s in songs:
        print(f"{s['id']:>2}. {s['title']} - {s['artist']} ({s['genre']}/{s['mood']})")


    # Taste profile: a "late-night study" listener who wants calm, mostly acoustic lofi.
    # Categorical keys are matched exactly; numeric targets are scored by closeness
    # (1 - |song value - target|), with tempo normalized by the 60-152 BPM range.
    user_prefs = {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.40,
        "likes_acoustic": True,        # treated as target acousticness of ~0.8
        "target_valence": 0.60,        # neutral-to-slightly-positive mood
        "target_danceability": 0.60,
        "target_tempo": 80,            # BPM
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
