import logging
import os
from typing import List, Tuple, Dict

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "recommender.log")


def _get_logger() -> logging.Logger:
    logger = logging.getLogger("recommender")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    os.makedirs(LOG_DIR, exist_ok=True)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(fmt)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def log_query(query: str) -> None:
    _get_logger().info("QUERY: %s", query)


def log_parsed_prefs(prefs: Dict) -> None:
    _get_logger().info("PARSED PREFS: %s", prefs)


def log_retrieved_songs(songs: List[Tuple[Dict, float, List[str]]]) -> None:
    logger = _get_logger()
    logger.info("RETRIEVED %d songs:", len(songs))
    for song, score, _ in songs:
        logger.info("  %.4f  %s — %s", score, song["title"], song["artist"])


def log_confidence(confidence: float) -> None:
    level = logging.WARNING if confidence < 0.6 else logging.INFO
    _get_logger().log(level, "PARSE CONFIDENCE: %.2f%s", confidence,
                      " — LOW CONFIDENCE, results may be inaccurate" if confidence < 0.6 else "")


def log_generated_response(response: str) -> None:
    _get_logger().info("GENERATED RESPONSE: %s", response)
