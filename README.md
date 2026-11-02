# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify and YouTube combine two kinds of signals. Collaborative filtering learns from what other users do (plays, skips, likes, playlist co-occurrence) to find songs that people with similar taste enjoy. Content-based filtering compares the attributes of the songs themselves (genre, mood, tempo, energy) to what a user has liked before. A ranking model then blends these with context, such as time of day and device, to predict engagement. My version is purely **content-based**: it has no listening history from other users, so it matches song attributes against a single user's stated taste. It prioritizes **genre and mood matches first**, then rewards songs whose **energy is close to the user's target** (closeness, not "higher is better"), with a smaller bonus for matching the user's acoustic preference.

### Song features

Each `Song` stores:

- `id`, `title`, `artist` (identification only, not scored)
- `genre` (categorical, scored)
- `mood` (categorical, scored)
- `energy` (0–1, scored by closeness to the user's target)
- `acousticness` (0–1, scored against the user's acoustic preference)
- `valence`, `danceability`, `tempo_bpm` (stored, but not scored in the base version because they overlap heavily with energy; candidates for later experiments)

### UserProfile features

Each `UserProfile` stores:

- `favorite_genre`
- `favorite_mood`
- `target_energy` (0–1)
- `likes_acoustic` (bool; treated as a target acousticness of about 0.8 if `True`, 0.2 if `False`)

### Algorithm Recipe

Every song in `data/songs.csv` is scored against the user's taste profile, and the points add up to a maximum of **5.0**:

| Component | Points | How it's calculated |
|---|---|---|
| Genre match | up to **+2.0** | 2.0 if `song.genre == favorite_genre`, else 0 |
| Mood match | up to **+1.0** | 1.0 if `song.mood == favorite_mood`, else 0 |
| Energy closeness | up to **+1.5** | `1.5 × (1 - abs(song.energy - target_energy))` |
| Acoustic closeness | up to **+0.5** | `0.5 × (1 - abs(song.acousticness - acoustic_target))`, where `acoustic_target` is 0.8 if `likes_acoustic` else 0.2 |

Numeric features are scored by **closeness to the user's target**, not by "higher is better", so a calm-music listener isn't handed the highest-energy songs. After scoring, all songs are sorted from highest to lowest and the top `k` are returned along with the reasons that contributed to each score (e.g. "genre match (lofi)", "energy 0.42 vs target 0.40").

**Why these weights:** genre is worth twice mood because it is the broader, more stable signal of taste, while mood is situational and partly overlaps with energy. Energy can outweigh mood (1.5 vs 1.0) so it acts as the main tiebreaker among songs in the same genre. Acousticness is a small nudge. Valence, danceability and tempo are stored but not scored, because in this dataset they are strongly correlated with energy and would mostly double-count it.

### Expected Biases and Limitations

- **Genre over-prioritization.** A genre match (+2.0) is worth more than any energy difference can offset (max 1.5), so a song in the user's genre will almost always outrank a better-fitting song from another genre. For a lofi/chill listener, *Spacewalk Thoughts* (ambient, chill, energy 0.28) scores about 2.8 while *Focus Flow* (lofi, "focused" mood) scores about 4.0, even though the ambient track may feel closer to what they want.
- **Exact string matching.** "pop" and "indie pop" count as completely different genres, and "chill", "relaxed" and "peaceful" count as completely different moods, even though listeners would treat them as near-neighbors.
- **Tiny, uneven catalog.** With 20 songs, most genres and moods appear exactly once (lofi has 3, everything else has 1-2). A user whose favorite genre is "rock" gets one genre match, and the rest of the list falls back to energy closeness. The system will look more "accurate" for lofi and pop users simply because there is more to choose from.
- **Double-counting intensity.** Energy and acousticness are correlated at about -0.99 in this data, so a user who wants calm music is effectively rewarded twice for the same trait.
- **Ignored features.** Valence (how positive a song sounds) is the one independent numeric feature and it is not scored, so two songs with the same energy but very different moods (e.g. *Gym Hero* vs. *Storm Runner*) are not distinguished unless the mood label differs.
- **One-dimensional, static taste.** `likes_acoustic` is a yes/no flag and the profile holds a single favorite genre and mood, so it can't represent someone who likes both jazz and metal, or whose taste changes by time of day.
- **No diversity or discovery.** The top `k` is just the `k` highest scores, so results can be dominated by one genre or artist, and there is no "explore" step like real platforms use.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



