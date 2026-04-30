# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeQuery 1.0**

---

## 2. Intended Use

VibeQuery is designed to recommend songs from a curated catalog based on how a person describes what they want to hear — in plain English. Instead of asking the user to fill out sliders or pick a genre from a dropdown, they just type something like "calm music for late-night studying" or "high energy for my morning run," and the system figures out the rest.

It is built for anyone who can describe a mood or moment but may not know the technical vocabulary of music — genre names, BPM ranges, energy levels. In that sense, it lowers the barrier to getting a useful recommendation.

The system assumes the user wants one of the moods and genres represented in the 20-song catalog. It works best when someone has a clear feeling they want to match. It does not learn from past interactions or remember what a user has listened to before — each query is treated as a fresh start.

This is a classroom project built for exploration and learning. It is not a production-ready application and the catalog is intentionally small.

---

## 3. How the Model Works

When a user types their request, the system runs three steps automatically.

**Step 1 — Understanding the request.** The system passes the user's words to a language model (Google Gemini). Gemini reads the sentence and translates it into a set of numbers and labels that describe musical taste: things like genre, mood, energy level (on a scale of 0 to 1), how danceable the song should be, how acoustic, and how fast the tempo should be. Gemini also rates how confident it is in that translation — if the request is too vague, it flags that as a warning.

**Step 2 — Finding the best matches.** The system compares those translated preferences against every song in the 20-song catalog using a scoring formula. Each song earns points based on how closely it matches: an exact genre match gives 3 points, an exact mood match gives 5 points (or 2.5 points if the song's mood falls in the same pre-defined cluster as the user's mood), and the numeric features contribute additional points weighted by importance — energy is worth up to 3 points, valence up to 2, and tempo, danceability, and acousticness up to 1, 1, and 0.5 respectively. The five songs with the highest total scores are returned.

**Step 3 — Explaining the results.** The top five songs — along with their scores and the specific reasons each song ranked where it did — are handed back to Gemini. Gemini then writes a short, conversational explanation of why each song fits what the user asked for. Crucially, it can only reference songs and scores that actually came from the catalog. It cannot invent songs or make up reasons.

The key change from the original version of this project is the first and third steps. Before, a developer had to type in the preference numbers manually. Now the user types a sentence, and the AI handles the translation in both directions — into structured data for the scorer, and back into natural language for the user.

---

## 4. Data

The catalog contains **20 songs**, each with the following attributes: title, artist, genre, mood, energy level, tempo in BPM, valence (how positive the feeling is), danceability, and acousticness.

The genres represented include pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, metal, reggae, country, r&b, EDM, blues, rap, afrobeats, and classical — though not all genres have equal representation. Lofi appears three times and pop twice, while niche genres like blues, reggae, and classical each appear only once.

The moods in the catalog span 16 options: happy, chill, intense, focused, moody, relaxed, peaceful, laid-back, euphoric, energetic, aggressive, melancholic, confident, nostalgic, sensual, and gritty.

No songs were removed from the original dataset. The catalog was designed for a classroom exercise and was not sourced from a real streaming service — the songs and artists are fictional.

The biggest gap in the dataset is breadth. Twenty songs is not enough to cover the full range of human musical taste. Someone who wants jazz specifically will likely receive pop songs in the lower-ranked results simply because jazz is one of the smaller categories. Moods like "romantic" or "dreamy" don't exist in the catalog at all, so Gemini has to approximate them with whatever comes closest — and that approximation is not always consistent.

---

## 5. Strengths

The system works best when the user's request is specific and maps cleanly to the catalog's vocabulary. Queries like "high energy workout music" or "calm lofi for studying" produce strong results because the scorer can award full mood and genre points, and the numeric features (energy, tempo) line up tightly with the catalog songs designed for those use cases.

The scoring formula captures **mood as the most important factor**, which reflects how most people actually think about music. If someone wants something chill, getting the mood right matters more than whether the tempo is exactly 80 BPM. The mood-first weighting (up to 5 points out of 15.5 possible) reflects that priority.

The system also does something the original version couldn't: it **explains why** a song was recommended in a way that feels natural to read. Users don't have to interpret numbers or feature labels — they get a sentence that references the specific aspects of the song that matched their request.

The **confidence guardrail** is a meaningful feature: when Gemini is uncertain about how to interpret a query, it says so, and the app surfaces that warning to the user rather than silently returning a potentially wrong result.

---

## 6. Limitations and Bias

**Catalog size.** With only 20 songs, the system will always return five results — but in many cases, only one or two are genuinely good matches. The rest fill the list by proximity, not by quality. A user who wants blues will likely see pop songs in positions three through five.

**Brittle mood vocabulary.** The scoring engine only awards mood points if the word Gemini returns exactly matches one of the 16 catalog mood labels, or is close enough to be in the same pre-defined cluster. Words like "romantic," "dreamy," or "uplifting" — which feel natural in everyday language — produce zero mood points because they don't appear in the catalog. The system can't tell the user this is why the results feel off.

**Genre overrepresentation.** Because pop songs make up a larger share of the catalog, a user whose genre preference doesn't match anything will likely see pop in the lower-ranked slots regardless of what they asked for. The ranking falls back to numeric similarity, but the genre column of the result will often say "pop."

**No personalization over time.** Every query starts from scratch. The system doesn't know what a user has already heard, what they liked or skipped, or how their taste has changed. A real recommendation system would improve over time; this one cannot.

**Self-reported confidence is not consistency.** Gemini rates its own confidence in each parse, but that number doesn't measure whether it would give the same answer twice. During testing, vague queries like "something romantic" produced a confidence of around 0.7 across multiple runs but returned different genres each time. The score measures certainty within one response, not stability across responses.

---

## 7. Evaluation

Three types of testing were used to check whether the system behaved as expected.

**Automated unit tests.** A test suite of 13 tests ran against the scoring logic directly, without calling the API. These included adversarial cases: what happens when a mood word isn't in any cluster, what happens when a song has a tempo so extreme it drives the tempo score negative, what happens when a user's numeric preferences are all zero. 12 out of 13 tests passed. The one failure was the test that calls the live API — it hit Gemini's free-tier daily rate limit, not a bug in the code.

**Manual live runs.** Three distinct query types were tested by running the app and reading the results: a high-energy query, a low-energy focused query, and an intentionally vague query ("something romantic"). The high-energy and low-energy runs produced results that matched intuition. The vague query triggered the low-confidence warning and returned reasonable but not obviously correct results — which is the expected behavior.

**Log review.** After each live run, the log file was checked to confirm that the parsed preferences Gemini returned actually matched what was described. This is where most of the interesting discoveries happened: on vague queries, the genre Gemini chose varied across runs even when the confidence score stayed the same. That finding was surprising enough to document as a known limitation.

What surprised me most was that the vague query "something romantic" produced a confidence of ~0.7 — which the system treats as acceptable and doesn't warn the user about — but the actual genre it mapped to was inconsistent run to run. The confidence score does not measure reproducibility.

---

## 8. Future Work

**Larger catalog.** The single most impactful improvement would be replacing the 20-song CSV with a real dataset — even a few hundred songs would dramatically improve result quality for niche genres. Connecting to a Spotify or Last.fm API would make the catalog live and much larger.

**Mood vocabulary expansion.** The hard-coded list of 16 mood words could be replaced with a semantic similarity approach — instead of checking if two words are in the same pre-defined cluster, compute how similar they are using embeddings. That way "romantic" and "sensual" would score partial credit automatically, without manual configuration.

**Playlist generation.** Right now the system returns five individual songs. A natural extension would be generating a coherent playlist — songs that flow well together, not just individually high-scoring ones. That would require reasoning about transitions, not just absolute scores.

**Memory across sessions.** Adding a user history component — even just a simple record of what genres and moods a user has queried before — would allow the system to break ties in favor of variety, preventing the same songs from appearing every time someone asks for a chill playlist.

**Handling contradictory requests.** A query like "something slow but high energy" is genuinely contradictory, and the current system can't flag that. A future version could detect when the parsed preferences are internally inconsistent and ask the user to clarify.

---

## 9. Personal Reflection

Building this project taught me that a recommendation system has two separate jobs: computing the right answer and communicating it in a way people can actually use. The original scoring engine did the first job well, but it was invisible — users couldn't tell why they were getting what they were getting. Adding the language model to the output layer made the system feel like something a real person could interact with, not just a tool a developer could inspect.

The most unexpected discovery was about confidence. I assumed that if the AI rated itself as 70% confident, that meant it was probably in the right territory. What I found was that confidence measures certainty within a single response — not whether it would say the same thing twice. Two identical queries returned different genres both rated at the same confidence level. That changed how I think about AI-generated metadata: a model's self-assessment is a data point, not a guarantee.

This project also changed how I think about music apps I use every day. Spotify and Apple Music are solving a much harder version of this problem — millions of songs, evolving taste, cross-device history, real audio signals — and the fact that they work as well as they do is genuinely impressive. Building a small version myself made me appreciate how much engineering is hidden behind a "For You" playlist.
