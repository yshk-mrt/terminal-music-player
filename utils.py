"""
Utilities Module
Contains utility functions for the music player.
"""

import os
import time
import math

def format_time(seconds):
    """Format seconds into a time string (MM:SS).
    
    Args:
        seconds: Number of seconds
        
    Returns:
        Formatted time string
    """
    if seconds is None or math.isnan(seconds):
        return "00:00"
    
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def format_file_size(size_bytes):
    """Format file size in bytes to a human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def get_terminal_size():
    """Get the terminal size.
    
    Returns:
        Tuple of (width, height)
    """
    try:
        columns, lines = os.get_terminal_size()
        return columns, lines
    except (AttributeError, OSError):
        # Fallback to default size
        return 80, 24

def truncate_string(string, max_length):
    """Truncate a string to a maximum length.
    
    Args:
        string: String to truncate
        max_length: Maximum length
        
    Returns:
        Truncated string
    """
    if len(string) <= max_length:
        return string
    
    # Truncate and add ellipsis
    return string[:max_length - 3] + "..."

def create_sample_music_files(directory):
    """Create sample music files for testing.
    
    This function creates valid MP3 files with metadata for testing
    when no music files are available.
    
    Args:
        directory: Directory to create sample files in
    """
    import mutagen.id3
    from mutagen.id3 import ID3, TIT2, TPE1, TALB
    from pydub import AudioSegment
    from pydub.generators import Sine
    
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Sample songs
    sample_songs = [
        {
            "title": "Sample Song 1",
            "artist": "Sample Artist 1",
            "album": "Sample Album 1",
            "filename": "sample_song_1.mp3",
            "frequency": 440,  # A4 note
            "duration": 3000   # 3 seconds
        },
        {
            "title": "Sample Song 2",
            "artist": "Sample Artist 2",
            "album": "Sample Album 2",
            "filename": "sample_song_2.mp3",
            "frequency": 523,  # C5 note
            "duration": 3000   # 3 seconds
        },
        {
            "title": "Sample Song 3",
            "artist": "Sample Artist 1",
            "album": "Sample Album 1",
            "filename": "sample_song_3.mp3",
            "frequency": 392,  # G4 note
            "duration": 3000   # 3 seconds
        }
    ]
    
    # Create sample files
    for song in sample_songs:
        file_path = os.path.join(directory, song["filename"])
        
        # Generate a simple tone
        print(f"Generating {song['filename']}...")
        sine_wave = Sine(song["frequency"])
        audio = sine_wave.to_audio_segment(duration=song["duration"])
        
        # Export as MP3
        audio.export(file_path, format="mp3")
        
        # Add metadata
        try:
            tags = ID3(file_path)
            tags.add(TIT2(encoding=3, text=song["title"]))
            tags.add(TPE1(encoding=3, text=song["artist"]))
            tags.add(TALB(encoding=3, text=song["album"]))
            tags.save(file_path)
            print(f"Added metadata to {file_path}")
        except Exception as e:
            print(f"Error adding metadata to {file_path}: {str(e)}")

def is_macos():
    """Check if the system is macOS.
    
    Returns:
        Boolean indicating if the system is macOS
    """
    return os.name == 'posix' and os.uname().sysname == 'Darwin'

def is_linux():
    """Check if the system is Linux.
    
    Returns:
        Boolean indicating if the system is Linux
    """
    return os.name == 'posix' and os.uname().sysname == 'Linux'

def is_windows():
    """Check if the system is Windows.
    
    Returns:
        Boolean indicating if the system is Windows
    """
    return os.name == 'nt'
