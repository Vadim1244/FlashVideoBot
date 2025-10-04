#!/usr/bin/env python3
"""
Test script to verify moviepy imports
"""

import os
import sys
print("Python executable:", sys.executable)
print("Python path:", sys.path)

print("\nTrying to import moviepy...")
try:
    import moviepy
    print("Moviepy imported successfully!")
    print("Moviepy version:", moviepy.__version__)
    print("Moviepy path:", moviepy.__file__)
except Exception as e:
    print(f"Error importing moviepy: {e}")

print("\nTrying to import moviepy.editor...")
try:
    import moviepy.editor
    print("Moviepy.editor imported successfully!")
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, ColorClip
    print("All required classes imported successfully!")
except Exception as e:
    print(f"Error importing moviepy.editor: {e}")

print("\nChecking if moviepy can create a simple clip...")
try:
    from moviepy.editor import ColorClip
    clip = ColorClip((640, 480), color=(0, 0, 255), duration=5)
    print("Created a color clip successfully!")
except Exception as e:
    print(f"Error creating clip: {e}")