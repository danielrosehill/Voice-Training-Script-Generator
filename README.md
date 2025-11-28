# Voice Training Script Generator

![alt text](image.png)

Generate reading scripts for voice cloning and TTS training data. Uses your measured words-per-minute (WPM) rate to create text that will take a specific duration to narrate.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- Gemini API key from https://aistudio.google.com/apikey

Install uv if not already installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup

```bash
# Set up API key
cp .env.example .env
# Edit .env and add your Gemini API key
```

The virtual environment and dependencies are automatically installed when you first run `./generate.sh`.

**Manual setup (optional):**
```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Get your Gemini API key at: https://aistudio.google.com/apikey

## Workflow

### 1. Measure Your WPM (Optional)

If you want accurate timing, first measure your speaking rate:

1. Place one or more MP3 files of yourself speaking in the `wpm-measure/` directory
2. Run the WPM calculator:

```bash
./calculate_wpm.py
```

3. Update `config.json` with your measured WPM

### 2. Generate Reading Scripts

Simply run:
```bash
./generate.sh
```

The script will prompt you for:
- Duration (in minutes)
- Style (select from numbered list)
- Number of chunks
- Optional topic focus

**Command-line mode** (for scripting):
```bash
# Basic: 30 minutes of conversational text in a single file
./generate.sh -d 30

# Specify a style
./generate.sh -d 30 -s narrative

# Split into multiple chunks (3 x 10-minute files)
./generate.sh -d 30 -c 3

# Specify chunk duration (automatically calculates number of chunks)
./generate.sh -d 30 --chunk-duration 10

# Add a topic focus
./generate.sh -d 60 -s technical -t "Python programming"

# Show help
./generate.sh --help
```

### Available Styles

- `conversational` - Natural, casual tone (default)
- `narrative` - Audiobook-style prose
- `technical` - Technical explanations and tutorials
- `news_anchor` - Professional broadcast style
- `storytelling` - Immersive fiction/stories
- `educational` - Documentary-style informative content
- `podcast` - Engaging monologue format

## Output

Generated scripts are saved to `output/session_<timestamp>/`:

```
output/session_20241128_150000/
├── script.txt          # Single file mode
├── chunk_01.txt        # Multi-chunk mode
├── chunk_02.txt
├── chunk_03.txt
└── metadata.json       # Generation details
```

## Configuration

Edit `config.json` to customize defaults:

```json
{
  "wpm": 198,
  "default_style": "conversational",
  "available_styles": [...],
  "default_chunk_duration_minutes": 10,
  "output_directory": "output"
}
```

## Directory Structure

```
.
├── calculate_wpm.py    # WPM measurement tool
├── generate_text.py    # Text generation script
├── generate.sh         # CLI wrapper (auto-installs venv)
├── config.json         # Configuration
├── requirements.txt    # Python dependencies
├── wpm-measure/        # Place audio samples here for WPM calculation
├── user-context/       # WPM analysis results
└── output/             # Generated scripts
```
