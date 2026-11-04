"""Rule-based analysis of tweet writing patterns."""

import json
import re
import string
from collections import Counter
from pathlib import Path
from typing import Iterable

from .tweets import Tweet

DEFAULT_PROFILE_PATH = Path("data") / "personality_profile.json"

_WORD_PATTERN = re.compile(r"[\w']+", re.UNICODE)
_UPPERCASE_WORD_PATTERN = re.compile(r"\b[A-Z]{2,}\b")
_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
    "did", "do", "for", "from", "had", "has", "have", "he", "her", "hers",
    "him", "his", "i", "if", "in", "into", "is", "it", "its", "me", "my",
    "of", "on", "or", "our", "ours", "she", "so", "than", "that", "the",
    "their", "them", "then", "there", "they", "this", "to", "up", "us", "was",
    "we", "were", "what", "when", "who", "will", "with", "you", "your",
}
_SLANG_TERMS = {
    "gonna", "idk", "lmao", "lol", "nah", "omg", "rn", "tbh", "wanna", "y'all",
}
_TOPIC_KEYWORDS = {
    "basketball": ("basketball", "fourth quarter", "defense", "coach", "rookie", "footwork", "buzzer beater"),
    "technology": ("keyboard", "laptop", "script", "computers", "app", "notification", "permissions"),
    "everyday life": ("coffee", "snacks", "laundry", "bus", "dog", "calendar", "water", "fridge", "rain"),
}
_HUMOR_CUES = ("😂", "🤣", "🙃", "lol", "lmao", "haha", "me:")
_OPINION_CUES = ("i love", "i hate", "i think", "i believe", "should", "wins games")


def _validate_tweets(tweets: Iterable[Tweet]) -> list[Tweet]:
    try:
        records = list(tweets)
    except TypeError as error:
        raise TypeError("tweets must be an iterable of Tweet records") from error

    for index, tweet in enumerate(records):
        if not isinstance(tweet, Tweet):
            raise TypeError(f"tweet at index {index} must be a Tweet record")
        if not isinstance(tweet.text, str) or not tweet.text.strip():
            raise ValueError(f"tweet at index {index} must have non-empty text")
        if not isinstance(tweet.tweet_id, str) or not tweet.tweet_id:
            raise ValueError(f"tweet at index {index} must have a non-empty ID")
    return records


def _top_phrases(tokens: list[str], minimum_size: int, maximum_size: int) -> list[dict[str, int | str]]:
    phrases: Counter[str] = Counter()
    for size in range(minimum_size, maximum_size + 1):
        for start in range(len(tokens) - size + 1):
            phrase_tokens = tokens[start : start + size]
            if not all(token in _STOP_WORDS for token in phrase_tokens):
                phrases[" ".join(phrase_tokens)] += 1
    return [
        {"phrase": phrase, "count": count}
        for phrase, count in sorted(phrases.items(), key=lambda item: (-item[1], item[0]))[:10]
    ]


def generate_personality_profile(tweets: Iterable[Tweet]) -> dict:
    """Return a JSON-compatible, evidence-labeled profile of tweet text."""
    records = _validate_tweets(tweets)
    texts = [tweet.text for tweet in records]
    token_lists = [[word.lower() for word in _WORD_PATTERN.findall(text)] for text in texts]
    all_tokens = [token for tokens in token_lists for token in tokens]
    content_words = [token for token in all_tokens if token not in _STOP_WORDS]
    word_counts = Counter(content_words)
    total_words = len(all_tokens)
    total_characters = sum(map(len, texts))
    uppercase_words = sum(len(_UPPERCASE_WORD_PATTERN.findall(text)) for text in texts)
    punctuation_counts = Counter(character for text in texts for character in text if character in string.punctuation)

    frequent_words = [
        {"word": word, "count": count}
        for word, count in sorted(word_counts.items(), key=lambda item: (-item[1], item[0]))[:10]
    ]
    slang_counts = Counter(
        token for token in all_tokens if token in _SLANG_TERMS
    )
    topics = []
    topic_examples: dict[str, Tweet] = {}
    for topic, keywords in _TOPIC_KEYWORDS.items():
        matches = [
            (tweet, keyword)
            for tweet in records
            for keyword in keywords
            if keyword in tweet.text.lower()
        ]
        if matches:
            topics.append({
                "topic": topic,
                "tweet_count": len({tweet.tweet_id for tweet, _ in matches}),
                "matched_keywords": sorted({keyword for _, keyword in matches}),
            })
            topic_examples[topic] = matches[0][0]

    humor_matches = [
        (tweet, cue)
        for tweet in records
        for cue in _HUMOR_CUES
        if cue in tweet.text.lower()
    ]
    opinion_matches = [
        tweet
        for tweet in records
        if any(cue in tweet.text.lower() for cue in _OPINION_CUES)
    ]

    def example(tweet: Tweet, aspect: str) -> dict[str, str]:
        return {"tweet_id": tweet.tweet_id, "text": tweet.text, "evidence_for": aspect}

    examples = []
    if records:
        examples.append(example(records[0], "representative sample"))
    if topic_examples:
        topic, tweet = next(iter(topic_examples.items()))
        if all(item["tweet_id"] != tweet.tweet_id for item in examples):
            examples.append(example(tweet, f"topic cue: {topic}"))
    if humor_matches:
        tweet = humor_matches[0][0]
        if all(item["tweet_id"] != tweet.tweet_id for item in examples):
            examples.append(example(tweet, "explicit humor cue"))

    has_data = bool(records)
    return {
        "dataset_context": {
            "classification": "synthetic sample data",
            "notice": "This profile describes only the supplied synthetic dataset, not the real owner's personality.",
        },
        "tweet_count": len(records),
        "communication_style": {
            "measured_patterns": {
                "average_characters": round(total_characters / len(records), 2) if has_data else None,
                "average_words": round(total_words / len(records), 2) if has_data else None,
                "uppercase_word_count": uppercase_words,
                "uppercase_word_rate": round(uppercase_words / total_words, 4) if total_words else None,
                "punctuation_counts": dict(sorted(punctuation_counts.items())),
            },
            "interpretation": "unknown; text metrics alone do not establish a stable personal communication style" if has_data else "unknown; no tweets supplied",
        },
        "vocabulary_patterns": {
            "frequently_used_words": frequent_words,
            "frequently_used_phrases": _top_phrases(all_tokens, 2, 3),
            "observed_slang_terms": [
                {"term": term, "count": count}
                for term, count in sorted(slang_counts.items())
            ],
            "slang_detection_note": "Counts use a small explicit slang list and are not an exhaustive vocabulary analysis.",
        },
        "frequently_discussed_topics": {
            "status": "observed" if topics else "unknown",
            "topics": topics,
            "method": "Keyword matches in the supplied tweet text; categories are limited and rule-based.",
        },
        "humor_characteristics": {
            "status": "explicit cues observed" if humor_matches else "unknown",
            "observable_cues": [
                {"tweet_id": tweet.tweet_id, "cue": cue}
                for tweet, cue in humor_matches
            ],
            "interpretation": "unknown; marker matches do not establish a person's general sense of humor",
        },
        "debate_style": {
            "status": "unknown",
            "evidence": [],
            "interpretation": "The supplied posts do not provide enough direct debate context to characterize debate style.",
        },
        "supported_opinions": {
            "status": "explicit wording observed" if opinion_matches else "unknown",
            "evidence": [example(tweet, "explicit opinion cue") for tweet in opinion_matches],
            "interpretation": "Only quoted posts with simple opinion cues are listed; broader beliefs are not inferred.",
        },
        "representative_examples": examples,
    }


def save_personality_profile(
    profile: dict,
    output_path: str | Path = DEFAULT_PROFILE_PATH,
) -> Path:
    """Write a generated profile as UTF-8 JSON and return its path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as profile_file:
        json.dump(profile, profile_file, ensure_ascii=False, indent=2)
        profile_file.write("\n")
    return path