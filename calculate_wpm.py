#!/usr/bin/env python3
"""
WPM Calculator - Calculates words per minute from audio files.

Uses Google Gemini API for transcription. Processes all MP3 files in the
wpm-measure folder and calculates average WPM if multiple files exist.

Requirements:
    pip install google-genai pydub python-dotenv

Environment:
    GEMINI_API_KEY - Your Google Gemini API key (can be set in .env file)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional if env vars are set directly

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package not installed.")
    print("Install with: pip install google-genai")
    sys.exit(1)

try:
    from pydub import AudioSegment
except ImportError:
    print("Error: pydub package not installed.")
    print("Install with: pip install pydub")
    sys.exit(1)


def get_audio_duration_seconds(file_path: Path) -> float:
    """Get the duration of an audio file in seconds using pydub."""
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000.0  # pydub returns milliseconds


def transcribe_audio(client: genai.Client, file_path: Path) -> str:
    """Transcribe audio file using Gemini API."""
    print(f"  Uploading {file_path.name}...")
    uploaded_file = client.files.upload(file=file_path)

    print(f"  Transcribing...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_uri(
                file_uri=uploaded_file.uri,
                mime_type="audio/mpeg"
            ),
            "Transcribe this audio exactly as spoken. "
            "Return ONLY the transcription text, nothing else."
        ]
    )

    return response.text.strip()


def count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def calculate_wpm(word_count: int, duration_seconds: float) -> float:
    """Calculate words per minute."""
    duration_minutes = duration_seconds / 60.0
    if duration_minutes == 0:
        return 0
    return word_count / duration_minutes


def main():
    # Setup paths
    script_dir = Path(__file__).parent
    wpm_measure_dir = script_dir / "wpm-measure"
    user_context_dir = script_dir / "user-context"
    output_file = user_context_dir / "wpm-analysis.json"

    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Get your API key from: https://aistudio.google.com/apikey")
        sys.exit(1)

    # Initialize Gemini client
    client = genai.Client(api_key=api_key)

    # Find MP3 files
    if not wpm_measure_dir.exists():
        print(f"Error: Directory not found: {wpm_measure_dir}")
        sys.exit(1)

    mp3_files = list(wpm_measure_dir.glob("*.mp3"))
    if not mp3_files:
        print(f"Error: No MP3 files found in {wpm_measure_dir}")
        sys.exit(1)

    print(f"Found {len(mp3_files)} MP3 file(s) to analyze.\n")

    # Process each file
    results = []
    for mp3_file in mp3_files:
        print(f"Processing: {mp3_file.name}")

        # Get duration
        duration = get_audio_duration_seconds(mp3_file)
        print(f"  Duration: {duration:.1f} seconds ({duration/60:.2f} minutes)")

        # Transcribe
        transcript = transcribe_audio(client, mp3_file)
        word_count = count_words(transcript)
        print(f"  Word count: {word_count}")

        # Calculate WPM
        wpm = calculate_wpm(word_count, duration)
        print(f"  WPM: {wpm:.1f}\n")

        results.append({
            "file": mp3_file.name,
            "duration_seconds": round(duration, 2),
            "word_count": word_count,
            "wpm": round(wpm, 1),
            "transcript": transcript
        })

    # Calculate average WPM
    average_wpm = sum(r["wpm"] for r in results) / len(results)
    total_words = sum(r["word_count"] for r in results)
    total_duration = sum(r["duration_seconds"] for r in results)

    # Prepare output
    output = {
        "analysis_date": datetime.now().isoformat(),
        "summary": {
            "files_analyzed": len(results),
            "total_words": total_words,
            "total_duration_seconds": round(total_duration, 2),
            "average_wpm": round(average_wpm, 1)
        },
        "files": results
    }

    # Create user-context directory and save results
    user_context_dir.mkdir(exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)

    # Print summary
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Files analyzed: {len(results)}")
    print(f"Total words: {total_words}")
    print(f"Total duration: {total_duration:.1f} seconds ({total_duration/60:.2f} minutes)")
    print(f"Average WPM: {average_wpm:.1f}")
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
