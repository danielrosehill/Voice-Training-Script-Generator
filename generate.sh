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

# Check for virtual environment
if [ -d "$VENV_DIR" ]; then
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

# Show help if no arguments
if [ $# -eq 0 ]; then
    echo "Voice Clone Text Generator"
    echo ""
    echo "Usage: $0 -d <duration_minutes> [options]"
    echo ""
    echo "Required:"
    echo "  -d, --duration      Target total duration in minutes"
    echo ""
    echo "Options:"
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
    echo ""
    echo "Examples:"
    echo "  $0 -d 30                              # 30 minutes, single file"
    echo "  $0 -d 30 -s narrative                 # 30 min narrative style"
    echo "  $0 -d 30 -c 3                         # 30 min in 3 chunks"
    echo "  $0 -d 30 --chunk-duration 10          # 30 min with 10-min chunks"
    echo "  $0 -d 60 -s technical -t 'AI basics'  # 60 min technical on AI"
    exit 0
fi

# Run the Python script with all arguments
python3 "$PYTHON_SCRIPT" "$@"
