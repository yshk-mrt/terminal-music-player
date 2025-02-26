#!/usr/bin/env python3
"""
Sample Music Creator
Creates sample music files for testing the Terminal Music Player.
"""

import os
import sys
from utils import create_sample_music_files

def main():
    """Main entry point for the sample creator."""
    # Default sample directory
    sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_music")
    
    # Check if a directory was provided
    if len(sys.argv) > 1:
        sample_dir = sys.argv[1]
    
    print(f"Creating sample music files in: {sample_dir}")
    create_sample_music_files(sample_dir)
    print("Sample music files created successfully!")
    print(f"Run the music player with: python main.py -d {sample_dir}")

if __name__ == "__main__":
    main()
