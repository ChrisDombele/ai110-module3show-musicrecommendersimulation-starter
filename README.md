# 🎵 Music Recommender Simulation

## Project Summary

YouTune 1.0 is a command-line music recommender. It loads a 20-song catalog, scores every song against a listener's taste profile (favorite genre, favorite mood, target energy and acoustic preference), and prints the top 5 matches with the reasons behind each score. It is content-based: it compares song attributes to stated preferences and uses no listening history. Testing with standard and adversarial profiles showed that it works well when preferences agree, but genre and mood labels can outvote the numeric preferences when they conflict.

---

## How The System Works

Real-world platforms like Spotify and YouTube combine two kinds of signals. Collaborative filtering learns from what other users do (plays, skips, likes, playlist co-occurrence) to find songs that people with similar taste enjoy. Content-based filtering compares the attributes of the songs themselves (genre, mood, tempo, energy) to what a user has liked before. A ranking model then blends these with context, such as time of day and device, to predict engagement. This version is purely **content-based**: it has no listening history from other users, so it matches song attributes against a single user's stated taste. It prioritizes **genre and mood matches first**, then rewards songs whose **energy is close to the user's target** (closeness, not "higher is better"), with a smaller bonus for matching the user's acoustic preference.

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

| Component          | Points         | How it's calculated                                                                                                 |
| ------------------ | -------------- | ------------------------------------------------------------------------------------------------------------------- |
| Genre match        | up to **+2.0** | 2.0 if `song.genre == favorite_genre`, else 0                                                                       |
| Mood match         | up to **+1.0** | 1.0 if `song.mood == favorite_mood`, else 0                                                                         |
| Energy closeness   | up to **+1.5** | `1.5 × (1 - abs(song.energy - target_energy))`                                                                      |
| Acoustic closeness | up to **+0.5** | `0.5 × (1 - abs(song.acousticness - acoustic_target))`, where `acoustic_target` is 0.8 if `likes_acoustic` else 0.2 |

Numeric features are scored by **closeness to the user's target**, not by "higher is better", so a calm-music listener isn't handed the highest-energy songs. After scoring, all songs are sorted from highest to lowest and the top `k` are returned along with the reasons that contributed to each score (e.g. "genre match (lofi)", "energy 0.42 vs target 0.40").

**Why these weights:** genre is worth twice mood because it is the broader, more stable signal of taste, while mood is situational and partly overlaps with energy. Energy can outweigh mood (1.5 vs 1.0) so it acts as the main tiebreaker among songs in the same genre. Acousticness is a small nudge. Valence, danceability and tempo are stored but not scored, because in this dataset they are strongly correlated with energy and would mostly double-count it.

### Expected Biases and Limitations

- **Genre over-prioritization.** A genre match (+2.0) is worth more than any energy difference can offset (max 1.5), so a song in the user's genre will almost always outrank a better-fitting song from another genre. For a lofi/chill listener, _Spacewalk Thoughts_ (ambient, chill, energy 0.28) scores about 2.8 while _Focus Flow_ (lofi, "focused" mood) scores about 4.0, even though the ambient track may feel closer to what they want.
- **Exact string matching.** "pop" and "indie pop" count as completely different genres, and "chill", "relaxed" and "peaceful" count as completely different moods, even though listeners would treat them as near-neighbors.
- **Tiny, uneven catalog.** With 20 songs, most genres and moods appear exactly once (lofi has 3, everything else has 1-2). A user whose favorite genre is "rock" gets one genre match, and the rest of the list falls back to energy closeness. The system will look more "accurate" for lofi and pop users simply because there is more to choose from.
- **Double-counting intensity.** Energy and acousticness are correlated at about -0.99 in this data, so a user who wants calm music is effectively rewarded twice for the same trait.
- **Ignored features.** Valence (how positive a song sounds) is the one independent numeric feature and it is not scored, so two songs with the same energy but very different moods (e.g. _Gym Hero_ vs. _Storm Runner_) are not distinguished unless the mood label differs.
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

   ```

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

Output from `python src/main.py` for the default taste profile (`favorite_genre="lofi"`, `favorite_mood="chill"`, `target_energy=0.40`, `likes_acoustic=True`) against the 20-song catalog:

```
Top recommendations:

Midnight Coding - Score: 4.92
Because: genre match: lofi (+2.00); mood match: chill (+1.00); energy closeness: 0.42 vs target 0.40 (+1.47); acousticness closeness: 0.71 vs target 0.80 (+0.45)

Library Rain - Score: 4.89
Because: genre match: lofi (+2.00); mood match: chill (+1.00); energy closeness: 0.35 vs target 0.40 (+1.42); acousticness closeness: 0.86 vs target 0.80 (+0.47)

Focus Flow - Score: 3.99
Because: genre match: lofi (+2.00); energy closeness: 0.40 vs target 0.40 (+1.50); acousticness closeness: 0.78 vs target 0.80 (+0.49)

Spacewalk Thoughts - Score: 2.76
Because: mood match: chill (+1.00); energy closeness: 0.28 vs target 0.40 (+1.32); acousticness closeness: 0.92 vs target 0.80 (+0.44)

Coffee Shop Stories - Score: 1.91
Because: energy closeness: 0.37 vs target 0.40 (+1.46); acousticness closeness: 0.89 vs target 0.80 (+0.46)
```

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

To see whether the scoring logic can be tricked, the recommender was run on seven adversarial or edge-case profiles. Each profile below shows the exact dictionary passed to `recommend_songs(profile, songs, k=5)` followed by the top 5 results from the terminal, then the observations.

### 1. Energetic but Sad

**Why it's tricky:** Conflicting preferences: a high-energy target paired with a mood (`sad`) that no song in the catalog has.

```
{'favorite_genre': 'pop', 'favorite_mood': 'sad', 'target_energy': 0.9, 'likes_acoustic': False}

Gym Hero (pop/intense, energy 0.93) - Score: 3.88
Because: genre match: pop (+2.00); energy closeness: 0.93 vs target 0.90 (+1.46); acousticness closeness: 0.05 vs target 0.20 (+0.42)

Sunrise City (pop/happy, energy 0.82) - Score: 3.87
Because: genre match: pop (+2.00); energy closeness: 0.82 vs target 0.90 (+1.38); acousticness closeness: 0.18 vs target 0.20 (+0.49)

Storm Runner (rock/intense, energy 0.91) - Score: 1.93
Because: energy closeness: 0.91 vs target 0.90 (+1.48); acousticness closeness: 0.10 vs target 0.20 (+0.45)

Calle Sol (latin/festive, energy 0.84) - Score: 1.91
Because: energy closeness: 0.84 vs target 0.90 (+1.41); acousticness closeness: 0.20 vs target 0.20 (+0.50)

Pulse Horizon (edm/euphoric, energy 0.95) - Score: 1.84
Because: energy closeness: 0.95 vs target 0.90 (+1.43); acousticness closeness: 0.04 vs target 0.20 (+0.42)
```

**Observation:** The `sad` mood matches nothing, so it is silently ignored. The two pop songs win on the genre bonus alone, and #2 is _Sunrise City_, a cheerful song, for someone who asked for sad. Gym Hero and Sunrise City are separated by 0.01 points, and everything else trails by about 2 points.

### 2. Genre vs Energy Conflict

**Why it's tricky:** Genre and mood point at the quietest song in the catalog while the energy target points at the loudest.

```
{'favorite_genre': 'classical', 'favorite_mood': 'melancholy', 'target_energy': 0.95, 'likes_acoustic': False}

Moonlit Reverie (classical/melancholy, energy 0.22) - Score: 3.52
Because: genre match: classical (+2.00); mood match: melancholy (+1.00); energy closeness: 0.22 vs target 0.95 (+0.41); acousticness closeness: 0.97 vs target 0.20 (+0.11)

Pulse Horizon (edm/euphoric, energy 0.95) - Score: 1.92
Because: energy closeness: 0.95 vs target 0.95 (+1.50); acousticness closeness: 0.04 vs target 0.20 (+0.42)

Gym Hero (pop/intense, energy 0.93) - Score: 1.90
Because: energy closeness: 0.93 vs target 0.95 (+1.47); acousticness closeness: 0.05 vs target 0.20 (+0.42)

Storm Runner (rock/intense, energy 0.91) - Score: 1.89
Because: energy closeness: 0.91 vs target 0.95 (+1.44); acousticness closeness: 0.10 vs target 0.20 (+0.45)

Iron Tide (metal/angry, energy 0.97) - Score: 1.89
Because: energy closeness: 0.97 vs target 0.95 (+1.47); acousticness closeness: 0.03 vs target 0.20 (+0.41)
```

**Observation:** _Moonlit Reverie_ wins with 3.52 even though its energy (0.22) is 0.73 away from the target and it is very acoustic for a user who dislikes acoustic music. The genre and mood bonuses (3.0 together) are worth more than a perfect energy match plus acoustic match (1.92, the runner-up). The stated energy target is effectively ignored.

### 3. Acoustic Fan Wants Max Energy

**Why it's tricky:** `likes_acoustic=True` combined with a genre, mood and energy target that no acoustic song can satisfy.

```
{'favorite_genre': 'edm', 'favorite_mood': 'euphoric', 'target_energy': 0.95, 'likes_acoustic': True}

Pulse Horizon (edm/euphoric, energy 0.95) - Score: 4.62
Because: genre match: edm (+2.00); mood match: euphoric (+1.00); energy closeness: 0.95 vs target 0.95 (+1.50); acousticness closeness: 0.04 vs target 0.80 (+0.12)

Gym Hero (pop/intense, energy 0.93) - Score: 1.60
Because: energy closeness: 0.93 vs target 0.95 (+1.47); acousticness closeness: 0.05 vs target 0.80 (+0.12)

Storm Runner (rock/intense, energy 0.91) - Score: 1.59
Because: energy closeness: 0.91 vs target 0.95 (+1.44); acousticness closeness: 0.10 vs target 0.80 (+0.15)

Iron Tide (metal/angry, energy 0.97) - Score: 1.58
Because: energy closeness: 0.97 vs target 0.95 (+1.47); acousticness closeness: 0.03 vs target 0.80 (+0.11)

Calle Sol (latin/festive, energy 0.84) - Score: 1.53
Because: energy closeness: 0.84 vs target 0.95 (+1.33); acousticness closeness: 0.20 vs target 0.80 (+0.20)
```

**Observation:** _Pulse Horizon_ wins with 4.62 while earning only +0.12 of the 0.5 acoustic points (acousticness 0.04 vs target 0.80). The acoustic preference is too small to matter, and nothing in the output warns that the request was contradictory. Ranks 2-5 are all non-acoustic, high-energy songs from other genres.

### 4. Genre Not In Catalog

**Why it's tricky:** A favorite genre that does not exist in the data.

```
{'favorite_genre': 'k-pop', 'favorite_mood': 'happy', 'target_energy': 0.7, 'likes_acoustic': False}

Rooftop Lights (indie pop/happy, energy 0.76) - Score: 2.83
Because: mood match: happy (+1.00); energy closeness: 0.76 vs target 0.70 (+1.41); acousticness closeness: 0.35 vs target 0.20 (+0.43)

Sunrise City (pop/happy, energy 0.82) - Score: 2.81
Because: mood match: happy (+1.00); energy closeness: 0.82 vs target 0.70 (+1.32); acousticness closeness: 0.18 vs target 0.20 (+0.49)

Night Drive Loop (synthwave/moody, energy 0.75) - Score: 1.91
Because: energy closeness: 0.75 vs target 0.70 (+1.42); acousticness closeness: 0.22 vs target 0.20 (+0.49)

Concrete Crown (hip hop/confident, energy 0.78) - Score: 1.84
Because: energy closeness: 0.78 vs target 0.70 (+1.38); acousticness closeness: 0.12 vs target 0.20 (+0.46)

Calle Sol (latin/festive, energy 0.84) - Score: 1.79
Because: energy closeness: 0.84 vs target 0.70 (+1.29); acousticness closeness: 0.20 vs target 0.20 (+0.50)
```

**Observation:** This one degrades gracefully: with no genre bonus available, mood and energy decide, and the top two (_Rooftop Lights_, _Sunrise City_) are reasonable picks for a happy, upbeat listener. The side effect is that the best possible score for this user is 3.0, not 5.0, so scores are not comparable across profiles.

### 5. Capitalization Mismatch

**Why it's tricky:** The same listener as the Chill Lofi profile, but with `Lofi` and `Chill` capitalized.

```
{'favorite_genre': 'Lofi', 'favorite_mood': 'Chill', 'target_energy': 0.4, 'likes_acoustic': True}

Focus Flow (lofi/focused, energy 0.4) - Score: 1.99
Because: energy closeness: 0.40 vs target 0.40 (+1.50); acousticness closeness: 0.78 vs target 0.80 (+0.49)

Midnight Coding (lofi/chill, energy 0.42) - Score: 1.92
Because: energy closeness: 0.42 vs target 0.40 (+1.47); acousticness closeness: 0.71 vs target 0.80 (+0.45)

Coffee Shop Stories (jazz/relaxed, energy 0.37) - Score: 1.91
Because: energy closeness: 0.37 vs target 0.40 (+1.46); acousticness closeness: 0.89 vs target 0.80 (+0.46)

Library Rain (lofi/chill, energy 0.35) - Score: 1.89
Because: energy closeness: 0.35 vs target 0.40 (+1.42); acousticness closeness: 0.86 vs target 0.80 (+0.47)

Smoky Blue Room (blues/bittersweet, energy 0.45) - Score: 1.86
Because: energy closeness: 0.45 vs target 0.40 (+1.42); acousticness closeness: 0.68 vs target 0.80 (+0.44)
```

**Observation:** Exact string matching is case-sensitive, so neither bonus applies and the top score falls from 4.92 to 1.99. _Library Rain_ (lofi/chill, the #2 song for the correct spelling) drops to #4, behind a jazz song. A harmless typo changes the results completely.

### 6. Impossible Energy (0.0)

**Why it's tricky:** A target energy below every song in the catalog (the minimum is 0.28).

```
{'favorite_genre': 'ambient', 'favorite_mood': 'chill', 'target_energy': 0.0, 'likes_acoustic': True}

Spacewalk Thoughts (ambient/chill, energy 0.28) - Score: 4.52
Because: genre match: ambient (+2.00); mood match: chill (+1.00); energy closeness: 0.28 vs target 0.00 (+1.08); acousticness closeness: 0.92 vs target 0.80 (+0.44)

Library Rain (lofi/chill, energy 0.35) - Score: 2.45
Because: mood match: chill (+1.00); energy closeness: 0.35 vs target 0.00 (+0.98); acousticness closeness: 0.86 vs target 0.80 (+0.47)

Midnight Coding (lofi/chill, energy 0.42) - Score: 2.33
Because: mood match: chill (+1.00); energy closeness: 0.42 vs target 0.00 (+0.87); acousticness closeness: 0.71 vs target 0.80 (+0.45)

Moonlit Reverie (classical/melancholy, energy 0.22) - Score: 1.58
Because: energy closeness: 0.22 vs target 0.00 (+1.17); acousticness closeness: 0.97 vs target 0.80 (+0.42)

Willow Lantern (folk/peaceful, energy 0.3) - Score: 1.47
Because: energy closeness: 0.30 vs target 0.00 (+1.05); acousticness closeness: 0.95 vs target 0.80 (+0.43)
```

**Observation:** This works as intended. Closeness scoring still ranks the lowest-energy songs first, and _Spacewalk Thoughts_ wins with a genre and mood match. Even the best song only earns 1.08 of the 1.5 energy points, so no song can reach the 5.0 maximum.

### 7. Middle of the Road (0.5)

**Why it's tricky:** A jazz fan who dislikes acoustic music, with a mid-range energy target.

```
{'favorite_genre': 'jazz', 'favorite_mood': 'relaxed', 'target_energy': 0.5, 'likes_acoustic': False}

Coffee Shop Stories (jazz/relaxed, energy 0.37) - Score: 4.46
Because: genre match: jazz (+2.00); mood match: relaxed (+1.00); energy closeness: 0.37 vs target 0.50 (+1.30); acousticness closeness: 0.89 vs target 0.20 (+0.16)

Velvet Hours (r&b/romantic, energy 0.5) - Score: 1.90
Because: energy closeness: 0.50 vs target 0.50 (+1.50); acousticness closeness: 0.40 vs target 0.20 (+0.40)

Island Breeze (reggae/carefree, energy 0.58) - Score: 1.76
Because: energy closeness: 0.58 vs target 0.50 (+1.38); acousticness closeness: 0.45 vs target 0.20 (+0.38)

Smoky Blue Room (blues/bittersweet, energy 0.45) - Score: 1.68
Because: energy closeness: 0.45 vs target 0.50 (+1.42); acousticness closeness: 0.68 vs target 0.20 (+0.26)

Dusty Back Roads (country/nostalgic, energy 0.55) - Score: 1.65
Because: energy closeness: 0.55 vs target 0.50 (+1.42); acousticness closeness: 0.74 vs target 0.20 (+0.23)
```

**Observation:** _Coffee Shop Stories_ wins with 4.46 even though its acousticness (0.89) is the opposite of what the user asked for; the genre and mood bonuses swamp it. There is only one jazz song, so the score falls off a cliff after #1 (4.46 to 1.90), and ranks 2-5 are mid-energy songs from unrelated genres separated by tiny margins.

### 8. Incomplete profile (missing key)

**Why it's tricky:** A profile that leaves out `likes_acoustic`.

```
recommend_songs({"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8}, songs, k=5)

  File "src/recommender.py", line 95, in score_song
    acoustic_target = ACOUSTIC_TARGET_LIKED if user_prefs["likes_acoustic"] else ACOUSTIC_TARGET_DISLIKED
KeyError: 'likes_acoustic'
```

**Observation:** `score_song` indexes the profile directly, so any missing key crashes the whole run instead of falling back to a default or skipping that component.

### Takeaways

- **Genre and mood dominate.** Together they are worth 3.0 points, while the energy and acoustic terms together are worth at most 2.0. Profiles 2, 3 and 7 show a genre/mood match beating a much better numeric fit.
- **Contradictions are resolved silently.** Profiles 1-3 contain conflicting preferences, and the output never flags that part of the request was ignored.
- **Unknown or mistyped labels fail quietly.** Profiles 1, 4 and 5 lose their genre or mood bonus with no warning, and 5 shows how fragile exact string matching is.
- **Scores are not comparable across users.** The achievable maximum differs by profile (profile 4 tops out at 3.0), so a raw score or a `score / 5.0` percentage would be misleading.
- **Things that held up.** Closeness scoring behaved sensibly for out-of-range targets (profile 6), and a missing genre fell back to mood plus energy (profile 4).
- **Possible fixes:** normalize strings with `.strip().lower()`, warn when a profile value matches nothing in the catalog, use `user_prefs.get(...)` with defaults, and lower the genre weight (the planned weight experiment).

### Weight Shift Experiment: halve genre, double energy

**Change:** in `src/recommender.py`, `GENRE_WEIGHT` 2.0 → 1.0 and `ENERGY_WEIGHT` 1.5 → 3.0 (mood 1.0 and acoustic 0.5 unchanged). `python src/main.py` and the seven edge-case profiles were run with this setting, then the original weights were restored, so the committed code and every other result in this README use the original recipe.

**Math check:** each component still lies between 0 and its weight (a 0–1 feature can't be more than 1.0 away from its target), so the maximum score is now the sum of the weights, **5.5 instead of 5.0**. Over 1,440 song/profile combinations the observed scores ranged from 0.21 to 5.40, the points listed in the "Because" reasons always added up to the score, and a song matching every preference scored exactly 5.5. The math stays valid, but scores are on a different scale (divide by 5.5 for a percentage), so they shouldn't be compared directly with the baseline numbers.

**Effect on the three standard profiles** (top-5 membership never changed):

| Profile           | Baseline order                                              | New order                                                   | #1 − #5 score gap |
| ----------------- | ----------------------------------------------------------- | ----------------------------------------------------------- | ----------------- |
| High-Energy Pop   | unchanged                                                   | unchanged                                                   | 3.09 → 2.13       |
| Chill Lofi        | unchanged                                                   | unchanged                                                   | 3.01 → 2.02       |
| Deep Intense Rock | Storm Runner, Gym Hero, Calle Sol, Pulse Horizon, Iron Tide | Storm Runner, Gym Hero, Pulse Horizon, Iron Tide, Calle Sol | 3.09 → 2.16       |

Terminal output with the shifted weights:

```
=== Top recommendations for High-Energy Pop ===

Sunrise City - Score: 5.40
Because: genre match: pop (+1.00); mood match: happy (+1.00); energy closeness: 0.82 vs target 0.85 (+2.91); acousticness closeness: 0.18 vs target 0.20 (+0.49)

Gym Hero - Score: 4.18
Because: genre match: pop (+1.00); energy closeness: 0.93 vs target 0.85 (+2.76); acousticness closeness: 0.05 vs target 0.20 (+0.42)

Rooftop Lights - Score: 4.16
Because: mood match: happy (+1.00); energy closeness: 0.76 vs target 0.85 (+2.73); acousticness closeness: 0.35 vs target 0.20 (+0.43)

Calle Sol - Score: 3.47
Because: energy closeness: 0.84 vs target 0.85 (+2.97); acousticness closeness: 0.20 vs target 0.20 (+0.50)

Storm Runner - Score: 3.27
Because: energy closeness: 0.91 vs target 0.85 (+2.82); acousticness closeness: 0.10 vs target 0.20 (+0.45)


=== Top recommendations for Chill Lofi ===

Midnight Coding - Score: 5.39
Because: genre match: lofi (+1.00); mood match: chill (+1.00); energy closeness: 0.42 vs target 0.40 (+2.94); acousticness closeness: 0.71 vs target 0.80 (+0.45)

Library Rain - Score: 5.32
Because: genre match: lofi (+1.00); mood match: chill (+1.00); energy closeness: 0.35 vs target 0.40 (+2.85); acousticness closeness: 0.86 vs target 0.80 (+0.47)

Focus Flow - Score: 4.49
Because: genre match: lofi (+1.00); energy closeness: 0.40 vs target 0.40 (+3.00); acousticness closeness: 0.78 vs target 0.80 (+0.49)

Spacewalk Thoughts - Score: 4.08
Because: mood match: chill (+1.00); energy closeness: 0.28 vs target 0.40 (+2.64); acousticness closeness: 0.92 vs target 0.80 (+0.44)

Coffee Shop Stories - Score: 3.37
Because: energy closeness: 0.37 vs target 0.40 (+2.91); acousticness closeness: 0.89 vs target 0.80 (+0.46)


=== Top recommendations for Deep Intense Rock ===

Storm Runner - Score: 5.42
Because: genre match: rock (+1.00); mood match: intense (+1.00); energy closeness: 0.91 vs target 0.92 (+2.97); acousticness closeness: 0.10 vs target 0.20 (+0.45)

Gym Hero - Score: 4.39
Because: mood match: intense (+1.00); energy closeness: 0.93 vs target 0.92 (+2.97); acousticness closeness: 0.05 vs target 0.20 (+0.42)

Pulse Horizon - Score: 3.33
Because: energy closeness: 0.95 vs target 0.92 (+2.91); acousticness closeness: 0.04 vs target 0.20 (+0.42)

Iron Tide - Score: 3.27
Because: energy closeness: 0.97 vs target 0.92 (+2.85); acousticness closeness: 0.03 vs target 0.20 (+0.41)

Calle Sol - Score: 3.26
Because: energy closeness: 0.84 vs target 0.92 (+2.76); acousticness closeness: 0.20 vs target 0.20 (+0.50)
```

**Effect on edge cases:** 5 of the 7 profiles kept exactly the same order, and _Acoustic Fan Wants Max Energy_ only swapped two lower slots (_Iron Tide_ and _Storm Runner_). The one that changed substantially is _Genre vs Energy Conflict_, where the quiet classical song fell out of the top 5 entirely:

```
=== Genre vs Energy Conflict ===
{'favorite_genre': 'classical', 'favorite_mood': 'melancholy', 'target_energy': 0.95, 'likes_acoustic': False}

Pulse Horizon (edm/euphoric, energy 0.95) - Score: 3.42
Because: energy closeness: 0.95 vs target 0.95 (+3.00); acousticness closeness: 0.04 vs target 0.20 (+0.42)

Gym Hero (pop/intense, energy 0.93) - Score: 3.37
Because: energy closeness: 0.93 vs target 0.95 (+2.94); acousticness closeness: 0.05 vs target 0.20 (+0.42)

Iron Tide (metal/angry, energy 0.97) - Score: 3.35
Because: energy closeness: 0.97 vs target 0.95 (+2.94); acousticness closeness: 0.03 vs target 0.20 (+0.41)

Storm Runner (rock/intense, energy 0.91) - Score: 3.33
Because: energy closeness: 0.91 vs target 0.95 (+2.88); acousticness closeness: 0.10 vs target 0.20 (+0.45)

Calle Sol (latin/festive, energy 0.84) - Score: 3.17
Because: energy closeness: 0.84 vs target 0.95 (+2.67); acousticness closeness: 0.20 vs target 0.20 (+0.50)
```

**More accurate, or just different?** Mostly just different. For listeners whose preferences agree with each other, the winners did not change; the gaps between ranks shrank, so songs from other genres that fit the energy target moved closer to the top (in High-Energy Pop, _Rooftop Lights_ went from 1.01 points behind _Gym Hero_ to 0.02 behind). That is a mild gain for discovery. For the conflicting profile the change did not fix the problem, it flipped it: the baseline ignored the user's energy request, and the new weights ignore their genre and mood request (classical/melancholy no longer appears at all). Which result is "right" depends on which preference the user cares about, and the system has no way to know. The takeaway is that the weights, not the data, decide whose preference wins a conflict.

---

## Limitations and Risks

### Limitations

- **Tiny catalog.** Only 20 songs, and most genres have a single song. A genre match gives that one song a large bonus, and a rock listener gets one strong match before scores drop from 4.93 to 2.91.
- **Fictional, hand-set data.** Songs, artists and feature values were written by hand. They are not measured from real audio.
- **No lyrics, language, release year or popularity.** Only genre, mood, energy and acousticness are scored. Valence, danceability and tempo are stored but not used.
- **Over-favors genre and mood.** Together they are worth 3.0 of 5.0 points, so they outvote the energy and acoustic preferences when a profile has conflicting wishes.
- **Exact text matching.** "Lofi" does not match "lofi", "pop" does not match "indie pop", and "chill" does not match "relaxed".
- **One static taste.** A profile holds a single favorite genre and mood, so it cannot represent someone who likes both jazz and metal, or whose taste changes by time of day.
- **Fragile input handling.** A profile missing `likes_acoustic` crashes the program with a `KeyError`.
- **Content-based only.** No listening history from other users is used, so the system cannot discover songs through "people like you also liked".

### Risks if this approach were scaled up

- **Filter bubbles.** The top results are simply the highest scores, so users keep getting more of the same genre with no exploration step.
- **Unequal service.** Users whose tastes are well covered by the catalog get much better lists than users whose genres are rare.
- **Silent failures.** When part of a request is ignored, the output does not say so, so users cannot tell why a recommendation looks wrong.
- **Hidden value judgments.** The weights decide whose preference wins a conflict. Changing them changes the results, but users never see or control them.
- **Exposure effects.** In a real product, scoring rules like these would decide which artists and genres get heard, and small bias in the weights could compound into large differences in exposure.

A deeper analysis is in the [model card](model_card.md), under **Limitations and Bias**.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

After working on this project, I learned a lot. An example would be how recommenders turn data into predictions. To go further into this, each song's genere, mood, energy, and acousticness are compared to the users preferences. Then it is converted into points which in turn is totaled into a sum that falls between 0 and 5.0. It was teh sorting of the scores that produced the recommendations. While working, I found that the bias or unfairness could show up in various places but experiments showed it in the weights. The genere and mood label were 3.0 points and the numeric features were at most 2.0. Any conflicts in preferences always resulted in leaning towards the labels.
