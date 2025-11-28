#!/bin/bash
#
# Voice Clone Text Generator - Shell wrapper
#
# Generates text scripts for voice recording based on target duration.
#
# Usage:
#   ./generate.sh -d <duration_minutes> [-s style] [-c chunks] [-t topic]
#
# Examples:
#   ./generate.sh -d 30                           # 30 min, single file, default style
#   ./generate.sh -d 30 -s narrative              # 30 min, narrative style
#   ./generate.sh -d 30 -c 3                      # 30 min split into 3 chunks (~10 min each)
#   ./generate.sh -d 30 --chunk-duration 10       # 30 min with 10 min chunks (= 3 chunks)
#   ./generate.sh -d 30 -s technical -t "Python"  # 30 min technical content about Python

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_SCRIPT="$SCRIPT_DIR/generate_text.py"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

# Setup virtual environment with uv if not present
if [ ! -d "$VENV_DIR" ]; then
    echo "Setting up virtual environment..."
    if ! command -v uv &> /dev/null; then
        echo "Error: uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    uv venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    echo "Installing dependencies..."
    uv pip install -r "$REQUIREMENTS"
else
    source "$VENV_DIR/bin/activate"
fi

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Check for required script
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: generate_text.py not found"
    exit 1
fi

# Interactive mode if no arguments
if [ $# -eq 0 ]; then
    echo "Voice Clone Text Generator"
    echo "=========================="
    echo ""

    # Duration
    read -p "Total duration in minutes: " DURATION
    if [ -z "$DURATION" ]; then
        echo "Error: Duration is required"
        exit 1
    fi

    # Style selection
    echo ""
    echo "Available styles:"
    echo "  1) conversational (default)"
    echo "  2) narrative"
    echo "  3) technical"
    echo "  4) news_anchor"
    echo "  5) storytelling"
    echo "  6) educational"
    echo "  7) podcast"
    echo ""
    read -p "Select style [1-7, default=1]: " STYLE_NUM

    case "$STYLE_NUM" in
        2) STYLE="narrative" ;;
        3) STYLE="technical" ;;
        4) STYLE="news_anchor" ;;
        5) STYLE="storytelling" ;;
        6) STYLE="educational" ;;
        7) STYLE="podcast" ;;
        *) STYLE="conversational" ;;
    esac

    # Chunks
    echo ""
    read -p "Number of chunks [default=1, single file]: " CHUNKS
    if [ -z "$CHUNKS" ]; then
        CHUNKS=1
    fi

    # Topic
    echo ""
    read -p "Topic focus [optional, press Enter to skip]: " TOPIC

    # Build command
    ARGS="-d $DURATION -s $STYLE"
    if [ "$CHUNKS" -gt 1 ]; then
        ARGS="$ARGS -c $CHUNKS"
    fi
    if [ -n "$TOPIC" ]; then
        ARGS="$ARGS -t \"$TOPIC\""
    fi

    echo ""
    echo "Generating ${DURATION} minutes of ${STYLE} content..."
    [ "$CHUNKS" -gt 1 ] && echo "Split into $CHUNKS chunks"
    [ -n "$TOPIC" ] && echo "Topic: $TOPIC"
    echo ""

    eval python3 "$PYTHON_SCRIPT" $ARGS
    exit $?
fi

# Show help with -h or --help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Voice Clone Text Generator"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Run without arguments for interactive mode."
    echo ""
    echo "Options:"
    echo "  -d, --duration      Target total duration in minutes"
    echo "  -s, --style         Text style:"
    echo "                        conversational (default)"
    echo "                        narrative"
    echo "                        technical"
    echo "                        news_anchor"
    echo "                        storytelling"
    echo "                        educational"
    echo "                        podcast"
    echo "  -c, --chunks        Number of separate files to generate"
    echo "  --chunk-duration    Duration per chunk in minutes (alternative to -c)"
    echo "  -t, --topic         Topic hint for content generation"
    echo "  --wpm               Override WPM from config"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Interactive mode"
    echo "  $0 -d 30                              # 30 minutes, single file"
    echo "  $0 -d 30 -s narrative                 # 30 min narrative style"
    echo "  $0 -d 30 -c 3                         # 30 min in 3 chunks"
    echo "  $0 -d 30 --chunk-duration 10          # 30 min with 10-min chunks"
    echo "  $0 -d 60 -s technical -t 'AI basics'  # 60 min technical on AI"
    exit 0
fi

# Run the Python script with all arguments
python3 "$PYTHON_SCRIPT" "$@"
