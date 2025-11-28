#!/usr/bin/env python3
"""
Text Generator for Voice Cloning - Generates reading scripts for voice recording.

Uses Google Gemini API to generate text for narration based on target duration
and reading style. Supports single file or chunked output.

Requirements:
    pip install google-genai python-dotenv

Environment:
    GEMINI_API_KEY - Your Google Gemini API key (can be set in .env file)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
except ImportError:
    print("Error: google-genai package not installed.")
    print("Install with: pip install google-genai")
    sys.exit(1)


def load_config(config_path: Path) -> dict:
    """Load configuration from config.json."""
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    with open(config_path) as f:
        return json.load(f)


def calculate_word_count(duration_minutes: float, wpm: int) -> int:
    """Calculate target word count from duration and WPM."""
    return int(duration_minutes * wpm)


def get_style_prompt(style: str) -> str:
    """Get the prompt modifier for a given style."""
    style_prompts = {
        "conversational": (
            "Write in a natural, conversational tone as if speaking to a friend. "
            "Include occasional filler words, natural pauses, and casual language. "
            "Topics can range widely - anecdotes, observations, musings."
        ),
        "narrative": (
            "Write engaging narrative prose suitable for an audiobook. "
            "Include descriptive passages, varied sentence structures, "
            "and compelling storytelling. Can be fiction or creative non-fiction."
        ),
        "technical": (
            "Write clear technical explanations or tutorials. "
            "Include precise terminology but maintain readability for narration. "
            "Topics can include technology, science, programming, or engineering."
        ),
        "news_anchor": (
            "Write in a professional news broadcast style. "
            "Clear, authoritative tone with good pacing for broadcast delivery. "
            "Include varied news topics - current events, features, human interest."
        ),
        "storytelling": (
            "Write immersive short stories or story excerpts. "
            "Include dialogue, scene descriptions, and emotional moments. "
            "Vary between action, reflection, and character development."
        ),
        "educational": (
            "Write informative educational content suitable for a documentary. "
            "Include interesting facts, clear explanations, and engaging delivery. "
            "Topics can span history, nature, culture, science."
        ),
        "podcast": (
            "Write in an engaging podcast monologue style. "
            "Include rhetorical questions, audience engagement phrases, "
            "and natural transitions between topics."
        )
    }
    return style_prompts.get(style, style_prompts["conversational"])


def generate_text_chunk(
    client: genai.Client,
    word_count: int,
    style: str,
    chunk_number: int = 1,
    total_chunks: int = 1,
    topic_hint: str = ""
) -> str:
    """Generate a single chunk of text using Gemini."""

    style_prompt = get_style_prompt(style)

    chunk_context = ""
    if total_chunks > 1:
        chunk_context = f"This is part {chunk_number} of {total_chunks}. "
        if chunk_number == 1:
            chunk_context += "Start fresh with an engaging opening. "
        elif chunk_number == total_chunks:
            chunk_context += "This is the final part - provide a satisfying conclusion. "
        else:
            chunk_context += "Continue naturally from a previous section. "

    topic_context = ""
    if topic_hint:
        topic_context = f"Focus on this topic area: {topic_hint}. "

    prompt = f"""Generate text for voice recording/narration.

Target word count: approximately {word_count} words (very important - aim for this count)

Style requirements:
{style_prompt}

{chunk_context}{topic_context}

Requirements:
- Generate ONLY the text to be read aloud
- No headers, titles, or metadata
- No stage directions or notes
- Natural flow suitable for continuous narration
- Varied sentence lengths for natural rhythm
- Avoid tongue-twisters or overly complex words
- Include natural breathing points (commas, periods)

Generate the text now:"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text.strip()


def save_output(
    output_dir: Path,
    texts: list[dict],
    style: str,
    total_duration: float,
    wpm: int
) -> Path:
    """Save generated texts to output directory."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = output_dir / f"session_{timestamp}"
    session_dir.mkdir(parents=True, exist_ok=True)

    # Save individual text files
    for i, text_data in enumerate(texts, 1):
        if len(texts) == 1:
            filename = "script.txt"
        else:
            filename = f"chunk_{i:02d}.txt"

        filepath = session_dir / filename
        with open(filepath, "w") as f:
            f.write(text_data["text"])

    # Save metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "style": style,
        "target_duration_minutes": total_duration,
        "wpm_used": wpm,
        "chunks": [
            {
                "file": f"chunk_{i:02d}.txt" if len(texts) > 1 else "script.txt",
                "target_word_count": t["target_words"],
                "actual_word_count": len(t["text"].split()),
                "estimated_duration_minutes": round(len(t["text"].split()) / wpm, 2)
            }
            for i, t in enumerate(texts, 1)
        ],
        "totals": {
            "total_words": sum(len(t["text"].split()) for t in texts),
            "estimated_total_duration_minutes": round(
                sum(len(t["text"].split()) for t in texts) / wpm, 2
            )
        }
    }

    metadata_path = session_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return session_dir


def main():
    parser = argparse.ArgumentParser(
        description="Generate reading scripts for voice cloning"
    )
    parser.add_argument(
        "-d", "--duration",
        type=float,
        required=True,
        help="Target total duration in minutes"
    )
    parser.add_argument(
        "-s", "--style",
        type=str,
        default=None,
        help="Text style (conversational, narrative, technical, news_anchor, storytelling, educational, podcast)"
    )
    parser.add_argument(
        "-c", "--chunks",
        type=int,
        default=1,
        help="Number of separate chunks to generate (default: 1 = single file)"
    )
    parser.add_argument(
        "--chunk-duration",
        type=float,
        default=None,
        help="Duration per chunk in minutes (alternative to --chunks)"
    )
    parser.add_argument(
        "-t", "--topic",
        type=str,
        default="",
        help="Optional topic hint for content generation"
    )
    parser.add_argument(
        "--wpm",
        type=int,
        default=None,
        help="Override WPM from config"
    )

    args = parser.parse_args()

    # Load config
    script_dir = Path(__file__).parent
    config = load_config(script_dir / "config.json")

    # Determine WPM
    wpm = args.wpm or config.get("wpm", 150)

    # Determine style
    style = args.style or config.get("default_style", "conversational")
    if style not in config.get("available_styles", [style]):
        print(f"Warning: Style '{style}' not in available styles. Using anyway.")

    # Calculate chunks
    if args.chunk_duration:
        num_chunks = max(1, int(args.duration / args.chunk_duration))
    else:
        num_chunks = args.chunks

    chunk_duration = args.duration / num_chunks

    # Check API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Get your API key from: https://aistudio.google.com/apikey")
        sys.exit(1)

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Print plan
    print("=" * 60)
    print("TEXT GENERATION PLAN")
    print("=" * 60)
    print(f"Total duration: {args.duration} minutes")
    print(f"Style: {style}")
    print(f"WPM: {wpm}")
    print(f"Chunks: {num_chunks}")
    print(f"Duration per chunk: {chunk_duration:.1f} minutes")
    print(f"Words per chunk: ~{calculate_word_count(chunk_duration, wpm)}")
    print(f"Total words: ~{calculate_word_count(args.duration, wpm)}")
    if args.topic:
        print(f"Topic hint: {args.topic}")
    print("=" * 60)
    print()

    # Generate chunks
    generated_texts = []
    for i in range(1, num_chunks + 1):
        target_words = calculate_word_count(chunk_duration, wpm)
        print(f"Generating chunk {i}/{num_chunks} (~{target_words} words)...")

        text = generate_text_chunk(
            client=client,
            word_count=target_words,
            style=style,
            chunk_number=i,
            total_chunks=num_chunks,
            topic_hint=args.topic
        )

        actual_words = len(text.split())
        print(f"  Generated {actual_words} words")

        generated_texts.append({
            "text": text,
            "target_words": target_words,
            "actual_words": actual_words
        })

    # Save output
    output_dir = script_dir / config.get("output_directory", "output")
    session_dir = save_output(output_dir, generated_texts, style, args.duration, wpm)

    # Summary
    total_actual = sum(t["actual_words"] for t in generated_texts)
    print()
    print("=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total words generated: {total_actual}")
    print(f"Estimated reading time: {total_actual / wpm:.1f} minutes")
    print(f"Output saved to: {session_dir}")
    print()
    print("Files created:")
    for f in sorted(session_dir.iterdir()):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
