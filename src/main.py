"""
Command line runner for the Music Recommender Simulation — RAG Edition.

Flow:
  1. User types a natural language query
  2. Claude (call #1) parses it into structured preferences
  3. recommend_songs() retrieves and scores the catalog
  4. Claude (call #2) generates a natural language explanation from the results
  5. Logger records every stage to logs/recommender.log
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs
from ai_client import parse_query, generate_explanation
from logger import log_query, log_parsed_prefs, log_confidence, log_retrieved_songs, log_generated_response

WIDTH = 54


def print_recommendation(rank: int, song: dict, score: float, reasons: list) -> None:
    bar = "─" * WIDTH
    title = song["title"]
    score_str = f"Score: {score:.2f}"
    gap = WIDTH - len(f"  #{rank}  {title}  {score_str}")
    header = f"  #{rank}  {title}{' ' * max(1, gap)}{score_str}"
    print(header)
    print(f"  {bar}")
    for reason in reasons:
        print(f"      • {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    print("\n  Music Recommender — RAG Edition")
    print(f"  {'═' * WIDTH}")
    query = input("\n  What do you want to hear? ").strip()
    if not query:
        print("  No input provided. Exiting.")
        return

    log_query(query)

    print("\n  Interpreting your request...")
    try:
        user_prefs, confidence = parse_query(query)
    except (ValueError, Exception) as e:
        print(f"\n  Could not parse your request: {e}")
        return

    log_parsed_prefs(user_prefs)
    log_confidence(confidence)

    if confidence < 0.6:
        print(f"\n  Warning: low confidence ({confidence:.0%}) — your request was unclear.")
        print("  Results may not match what you had in mind.\n")

    recommendations = recommend_songs(user_prefs, songs, k=5)
    log_retrieved_songs(recommendations)

    print(f"\n  Top {len(recommendations)} Recommendations")
    print(f"  {'═' * WIDTH}\n")
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        print_recommendation(rank, song, score, reasons)

    print(f"  {'─' * WIDTH}")
    print("  Why these songs?\n")
    try:
        explanation = generate_explanation(query, recommendations)
    except Exception as e:
        explanation = f"(Could not generate explanation: {e})"

    log_generated_response(explanation)

    for line in explanation.splitlines():
        print(f"  {line}")
    print()


if __name__ == "__main__":
    main()
