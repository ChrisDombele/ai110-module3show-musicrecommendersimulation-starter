# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**YouTune 1.0**

---

## 2. Intended Use

**Goal / Task**

YouTune suggests songs for one listener. It looks at a small catalog and picks the 5 songs that best match that person's taste. It gives every song a match score. It also explains each score in plain words.

The listener gives four inputs: a favorite genre, a favorite mood, a target energy level, and whether they like acoustic music.

**Intended use**

- To learn how a scoring recommender works.
- It runs in the terminal with `python src/main.py`.

**Assumptions about the user**

- The user knows their taste and can describe it with four settings.
- The user has one favorite genre and one favorite mood.
- Their taste does not change by time of day or situation.

**Not intended for**

- A real music app or real listeners. The catalog is far too small.
- Judging whether a song is good or bad.
- Any decision that affects people, such as pay, hiring, or what artists get exposure.
- Learning from listening history. It does not do that.
- Claiming what people "should" listen to.

---

## 3. How the Model Works

Every song in the catalog earns points. The songs with the most points are shown first. The most any song can earn is 5 points.

| Rule                                                     | Points    |
| -------------------------------------------------------- | --------- |
| The song's genre is the user's favorite genre            | 2.0       |
| The song's mood is the user's favorite mood              | 1.0       |
| The song's energy is close to the user's target energy   | up to 1.5 |
| The song's acoustic feel is close to what the user likes | up to 0.5 |

- **Closeness, not "more is better."** A song with energy right at the target gets the full 1.5. A song far from the target gets close to 0. So a user who wants calm music is not given loud songs.
- **Acoustic taste.** If the user likes acoustic music, the model aims for a very acoustic song. If not, it aims for a song that is not acoustic.
- **Reasons.** Each song comes with a list of why it scored that way. For example: "genre match: lofi (+2.00)".
- **Why genre counts the most.** Genre is a broad, steady sign of taste. Mood changes with the moment, and it overlaps with energy.
- **What is not scored.** Tempo, valence, and danceability are in the data. They are left out because they move together with energy. Scoring them would count the same thing twice.

---

## 4. Data

- **Size:** 20 songs in `data/songs.csv`.
- **Columns:** id, title, artist, genre, mood, energy, tempo (BPM), valence, danceability, and acousticness. Energy, valence, danceability, and acousticness run from 0 to 1. Tempo is in beats per minute.
- **Genres:** 17 in total. Lofi has 3 songs and pop has 2. Every other genre has 1.
- **Moods:** 16 in total. Chill has 3 songs, happy and intense have 2 each. Every other mood has 1.
- **What was added:** The starter had 10 songs. Ten more were added, with new genres and moods. They are hip hop, classical, country, r&b, metal, reggae, edm, folk, blues, and latin.
- **The data is made up.** The songs and artists are fictional. The numbers were set by hand. They are not measured from real audio.

**What is missing**

- Lyrics, language, release year, and popularity.
- Most genres from around the world. There is no K-pop, for example.
- Listening history from real people.
- Enough songs per genre. One song per genre is not enough to rank anything.

---

## 5. Strengths

The system works best when the user's four choices agree with each other.

- **Chill Lofi listener:** the top 3 songs are all lofi, and the scores are 4.92, 4.89, and 3.99. That matched expectations.
- **Pop and rock listeners:** the #1 song fits well. _Sunrise City_ is first for pop. _Storm Runner_ is first for rock.
- **Calm users stay calm.** Closeness scoring means a user who wants low energy does not get loud songs.
- **Clear reasons.** Each result lists the points it earned. It is easy to see why a song ranked where it did.
- **Odd inputs.** An energy target below every song still gave sensible results. A genre that is not in the catalog fell back to mood and energy.
- **Similar users get similar lists.** Two high-energy users shared three songs. Two calm users shared three songs.

---

## 6. Limitations and Bias

**Biggest problem: labels outvote numbers.**

- A genre match plus a mood match gives 3.0 points. Energy and acousticness give at most 2.0 together.
- So when a user's wishes conflict, the labels win and the numbers lose.
- Test: a user asked for classical and melancholy, but energy 0.95. The quiet classical song _Moonlit Reverie_ still ranked #1 at 3.52. Its energy was 0.73 away from the target.
- Genre was halved and energy was doubled. That flipped the problem. The classical song left the top 5, and the genre request was ignored instead.
- The weights decide whose wish wins. The data does not.

**Other limits**

- **Tiny catalog.** Most genres have one song. A genre match hands that one song a big bonus.
- **Uneven catalog.** Lofi fans get three strong matches. Rock fans get one, and then the scores fall from 4.93 to 2.91.
- **Exact text only.** "Lofi" does not match "lofi". "Pop" does not match "indie pop". "Chill" does not match "relaxed".
- **Silent failures.** If part of a request is ignored, the system does not say so.
- **Double counting.** Energy and acousticness move together (correlation about -0.99). Calm users get rewarded twice for one trait.
- **Ignored features.** Valence, tempo, and danceability are not scored.
- **One taste only.** A user can have one genre and one mood. Someone who likes both jazz and metal is not supported.

---

## 7. Evaluation

The recommender was checked by running it on three ordinary profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock) and then on seven adversarial or edge-case profiles designed to trick the scoring logic. For each one, the top 5 and the "Because" reasons were read and compared with what that listener would plausibly want. The full terminal output for every edge-case profile is pasted in the README under **Experiments You Tried**.

**Profiles tested and what happened**

| #   | Profile                                                                   | What it tests                                         | Result                                                                                                                      |
| --- | ------------------------------------------------------------------------- | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| 1   | Energetic but Sad (pop, mood `sad`, energy 0.9)                           | Conflicting preferences; a mood not in the catalog    | `sad` is silently ignored. Pop songs win on genre alone, and a cheerful song (_Sunrise City_) is #2.                        |
| 2   | Genre vs Energy Conflict (classical/melancholy, energy 0.95)              | Genre and mood pulling against the energy target      | The quiet classical song wins at 3.52 even though its energy is 0.73 off target. The energy request is effectively ignored. |
| 3   | Acoustic Fan Wants Max Energy (edm/euphoric, energy 0.95, likes acoustic) | A contradictory acoustic preference                   | _Pulse Horizon_ wins at 4.62 with an acousticness of 0.04. The acoustic term is too small to matter.                        |
| 4   | Genre Not In Catalog (k-pop)                                              | A genre that matches nothing                          | Degrades gracefully to mood plus energy. Sensible results, but the best possible score is only 3.0.                         |
| 5   | Capitalization Mismatch (`Lofi`, `Chill`)                                 | Brittle exact string matching                         | Both bonuses vanish. The top score drops from 4.92 to 1.99, and _Library Rain_ falls behind a jazz song.                    |
| 6   | Impossible Energy (0.0)                                                   | A target below every song                             | Behaves sensibly; the lowest-energy songs rank first.                                                                       |
| 7   | Middle of the Road (jazz/relaxed, energy 0.5, dislikes acoustic)          | A one-song genre and a preference the winner violates | _Coffee Shop Stories_ wins at 4.46 despite being very acoustic, then scores drop to 1.90 for #2.                            |
| 8   | Incomplete profile (no `likes_acoustic`)                                  | Missing input                                         | Crashes with `KeyError: 'likes_acoustic'`.                                                                                  |

**What was looked for:** whether results followed the closeness logic, whether a contradictory profile was handled or at least flagged, and whether a small change in how a preference was written (capitalization, unknown label) changed the results.

**Surprises:**

- Genre and mood together (3.0 points) outweigh the two numeric features combined (2.0 points), so for a user with conflicting preferences the numeric targets lose almost every time (profiles 2, 3 and 7).
- The system never tells the user that part of the request was ignored. A listener who asks for "sad" and gets upbeat pop would have no way to know why.
- The `Capitalization Mismatch` profile shows how a trivial input difference can reduce a good recommender to a near-random one.
- Scores are not comparable between users, because the maximum reachable score depends on which labels exist in the catalog.

**What worked well:** the closeness scoring handled an out-of-range energy target correctly (profile 6), and a missing genre fell back to mood and energy rather than failing (profile 4).

**Comparing pairs of profiles**

Each comparison asks whether the difference in output matches the difference in what the two users asked for.

- **Chill Lofi vs. High-Energy Pop:** the top 5 lists share no songs. Chill Lofi gets songs with energy 0.28-0.42 and acousticness 0.71-0.92, while High-Energy Pop gets energy 0.76-0.93 and acousticness 0.05-0.35. That makes sense, because the two profiles are opposite on energy (0.40 vs. 0.85) and on the acoustic preference, and the scoring responds to both.
- **High-Energy Pop vs. Deep Intense Rock:** both want high energy, so three songs appear in both lists (_Gym Hero_, _Calle Sol_, _Storm Runner_). The #1 picks differ because of the labels: _Sunrise City_ (pop, happy) for pop and _Storm Runner_ (rock, intense) for rock. _Gym Hero_ is #2 for both for different reasons: it earns the genre bonus for the pop user and the mood bonus for the rock user. This is valid, since both users want loud songs and differ only in genre and mood.
- **Chill Lofi vs. Deep Intense Rock:** opposite ends of the energy scale and no overlap. The difference in list quality is also informative: Chill Lofi has three strong matches (4.92, 4.89, 3.99) because the catalog has three lofi songs, while Rock drops from 4.93 to 2.91 after its single rock song. The scoring is fine here, but the catalog gives lofi listeners a better experience than rock listeners.
- **Chill Lofi vs. Capitalization Mismatch (`Lofi`/`Chill`):** the same listener typed two ways. The top score falls from 4.92 to 1.99, and _Library Rain_ goes from #2 to #4, behind a jazz song. This is not a valid difference, because the user's taste did not change; it exposes the exact string matching.
- **High-Energy Pop vs. Energetic but Sad:** nearly the same energy target (0.85 vs. 0.90) and both pop; they differ in mood (`happy` vs. `sad`). With `happy`, _Sunrise City_ wins 4.95 to 3.80. With `sad`, which matches nothing, _Gym Hero_ and _Sunrise City_ are essentially tied (3.88 vs. 3.87). The 1.0 mood bonus is the only thing separating them, which confirms that mood works, but it also shows the user's `sad` request does nothing.
- **High-Energy Pop vs. Genre Not In Catalog (`k-pop`, happy, 0.70):** with the pop genre bonus unavailable, _Rooftop Lights_ (indie pop, happy) takes #1 instead of _Sunrise City_. That is a sensible outcome, since indie pop is the closest neighbor, but it only happens because the exact genre is missing; it would never beat a plain pop song for a pop fan.
- **Chill Lofi vs. Impossible Energy (ambient, chill, energy 0.0):** both want quiet, acoustic, chill songs, and three songs appear in both lists (_Spacewalk Thoughts_, _Library Rain_, _Midnight Coding_). Only the winner changes (_Midnight Coding_ vs. _Spacewalk Thoughts_), because the genre bonus moves from lofi to ambient. This is the intended behavior.
- **Genre vs Energy Conflict vs. Acoustic Fan Wants Max Energy:** four of the five songs in the two lists are the same loud songs (_Pulse Horizon_, _Gym Hero_, _Storm Runner_, _Iron Tide_), even though one user dislikes acoustic music and the other likes it. Once the label match is used up on #1, only the energy term separates the rest, and the acoustic term is too weak (at most 0.5) to reorder them. So the acoustic preference is barely tested by this scoring.
- **Chill Lofi vs. Middle of the Road (jazz, relaxed, 0.5):** _Coffee Shop Stories_ is #5 for Chill Lofi (1.91) and #1 for Middle of the Road (4.46). Its energy and acousticness barely changed the score; the genre and mood labels moved it from last place to first, even though this user said they dislike acoustic songs and it is among the most acoustic in the catalog.

**Sensitivity test (halve genre, double energy):** The genre weight was changed from 2.0 to 1.0 and the energy weight from 1.5 to 3.0, and the maximum score became 5.5. The standard profiles kept their top picks and only shuffled lower slots, and the gaps between ranks narrowed. The classical profile changed the most, losing its #1 song entirely. The change made the results different rather than clearly more accurate. The full output is in the README under **Experiments You Tried**.

**Possible fixes:** normalize strings before comparing, warn when a profile value matches nothing in the catalog, use defaults for missing profile keys, and test a middle setting between the two weightings (genre 1.5, energy 2.0) to see whether it avoids ignoring either preference.

---

## 8. Future Work

1. **Clean up the input.** Ignore capital letters and extra spaces. Warn the user when a genre or mood is not in the catalog. Use a default when a setting is missing, so the program does not crash.
2. **Give partial credit.** Let similar labels earn some points. Pop and indie pop could earn 1.0 of the 2.0. Chill and relaxed could earn half of the mood points. Also score valence, since it is the one feature that does not overlap with energy.
3. **Add more songs and more variety.** Add several songs per genre. Keep one genre from filling the whole top 5. Let a user pick more than one favorite genre.

---

## 9. Personal Reflection

Before this project, I used to think there was a lot more to recommendation apps or features in apps like spotify or youtube. I am not saying that what I accomplished with this project is not comlex but seeing the building blocks of algorithmic recommendations makes it seem simple. The comlexity of course comes from the enormous amount of data from million of users and combining different metrics and scores. What I found most interesting about this project is the balance it takes to create a system like this. Any part of the algorithm can easiy skew the results and lead to bias. I also find it interesting how you can either create, like a score via an algorithm, or take different pre existing data points on music to create recommendations. This project has taught me a lot about recommender systems. Everything from the type of data that should be included for input, to the algorithm that outputs the recommendations. I think the most important piece of the system is the song score algorithm and how it uses user preferences to generate a score to rank songs that were loaded in.
