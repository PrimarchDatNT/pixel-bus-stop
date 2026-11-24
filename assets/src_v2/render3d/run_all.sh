#!/bin/zsh
# full pipeline: render passes with Blender, post-process, compose
cd "$(dirname "$0")"
SPP=${SPP:-200} /Applications/Blender.app/Contents/MacOS/Blender -b -P render.py -- ground facades shelter bus cat 2>&1 | grep -E "Error|Traceback|rendered"
../../../.venv/bin/python post.py && ../../../.venv/bin/python compose.py
