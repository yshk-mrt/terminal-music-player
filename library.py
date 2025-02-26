"""
Music Library Module
Handles scanning for music files and managing the music collection.
"""

import os
import re
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
from rich.console import Console

class MusicLibrary:
    """Music library class for managing the music collection."""
    
    SUPPORTED_FORMATS = ('.mp3', '.flac', '.ogg', '.wav')
    
    def __init__(self, music_dir):
        """Initialize the music library.
        
        Args:
            music_dir: Directory containing music files
        """
        self.music_dir = os.path.expanduser(music_dir)
        self.songs = []
        self.console = Console()
        
        # Scan for music files
        self._scan_music_files()
    
    def _scan_music_files(self):
        """Scan the music directory for supported audio files."""
        self.console.print(f"[cyan]Scanning for music in:[/cyan] {self.music_dir}")
        
        if not os.path.exists(self.music_dir):
            self.console.print(f"[yellow]Warning:[/yellow] Music directory does not exist: {self.music_dir}")
            return
        
        # Clear existing songs
        self.songs = []
        
        # Walk through the directory
        for root, _, files in os.walk(self.music_dir):
            for file in files:
                if file.lower().endswith(self.SUPPORTED_FORMATS):
                    file_path = os.path.join(root, file)
                    song_info = self._extract_metadata(file_path)
                    if song_info:
                        self.songs.append(song_info)
        
        # Sort songs by artist and title
        self.songs.sort(key=lambda x: (x.get('artist', ''), x.get('title', '')))
        
        self.console.print(f"[green]Found {len(self.songs)} songs[/green]")
    
    def _extract_metadata(self, file_path):
        """Extract metadata from an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary containing song metadata
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Default metadata
            metadata = {
                'path': file_path,
                'title': os.path.basename(file_path),
                'artist': 'Unknown Artist',
                'album': 'Unknown Album',
                'length': 0
            }
            
            # Extract metadata based on file type
            if file_ext == '.mp3':
                audio = MP3(file_path)
                if audio.tags:
                    if 'TIT2' in audio.tags:
                        metadata['title'] = str(audio.tags['TIT2'])
                    if 'TPE1' in audio.tags:
                        metadata['artist'] = str(audio.tags['TPE1'])
                    if 'TALB' in audio.tags:
                        metadata['album'] = str(audio.tags['TALB'])
                metadata['length'] = audio.info.length
                
            elif file_ext == '.flac':
                audio = FLAC(file_path)
                if 'title' in audio:
                    metadata['title'] = audio['title'][0]
                if 'artist' in audio:
                    metadata['artist'] = audio['artist'][0]
                if 'album' in audio:
                    metadata['album'] = audio['album'][0]
                metadata['length'] = audio.info.length
                
            elif file_ext == '.ogg':
                audio = OggVorbis(file_path)
                if 'title' in audio:
                    metadata['title'] = audio['title'][0]
                if 'artist' in audio:
                    metadata['artist'] = audio['artist'][0]
                if 'album' in audio:
                    metadata['album'] = audio['album'][0]
                metadata['length'] = audio.info.length
                
            elif file_ext == '.wav':
                audio = WAVE(file_path)
                # WAV files typically don't have metadata
                metadata['length'] = audio.info.length
            
            # Clean up title if no metadata was found
            if metadata['title'] == os.path.basename(file_path):
                # Try to extract a nicer title from the filename
                filename = os.path.splitext(os.path.basename(file_path))[0]
                # Remove track numbers (e.g., "01 - " or "01.")
                filename = re.sub(r'^\d+[\s.-]+', '', filename)
                metadata['title'] = filename
            
            return metadata
            
        except Exception as e:
            self.console.print(f"[yellow]Warning:[/yellow] Could not read metadata from {file_path}: {str(e)}")
            return None
    
    def refresh(self):
        """Refresh the music library by rescanning the music directory."""
        self._scan_music_files()
    
    def get_song_by_index(self, index):
        """Get a song by its index in the library.
        
        Args:
            index: Index of the song
            
        Returns:
            Dictionary containing song metadata or None if index is invalid
        """
        if 0 <= index < len(self.songs):
            return self.songs[index]
        return None
    
    def search(self, query):
        """Search for songs matching the query.
        
        Args:
            query: Search query string
            
        Returns:
            List of songs matching the query
        """
        if not query:
            return self.songs
        
        query = query.lower()
        results = []
        
        for song in self.songs:
            if (query in song['title'].lower() or 
                query in song['artist'].lower() or 
                query in song['album'].lower()):
                results.append(song)
        
        return results
    
    def get_song_count(self):
        """Get the number of songs in the library.
        
        Returns:
            Integer representing the number of songs
        """
        return len(self.songs)
