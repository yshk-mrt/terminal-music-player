"""
Music Player Module
Handles audio playback functionality using pygame.
"""

import os
import time
import threading
import pygame
import numpy as np
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE

class MusicPlayer:
    """Music player class for handling audio playback."""
    
    def __init__(self, library):
        """Initialize the music player.
        
        Args:
            library: MusicLibrary instance containing the music collection
        """
        self.library = library
        self.current_song_index = 0
        self.playing = False
        self.paused = False
        self.volume = 0.7  # Default volume (0.0 to 1.0)
        self.audio_data = None
        self.visualizer_data = np.zeros(64)
        self._visualizer_thread = None
        self._stop_visualizer = threading.Event()
        
        # Initialize pygame mixer
        pygame.mixer.init(frequency=44100)
        
    def play(self):
        """Play the current song."""
        if not self.library.songs:
            raise ValueError("No songs available in the library")
        
        current_song = self.library.songs[self.current_song_index]
        
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.playing = True
            return
        
        try:
            pygame.mixer.music.load(current_song['path'])
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            self.playing = True
            self.paused = False
            
            # Start visualizer data generation
            self._start_visualizer()
            
        except pygame.error as e:
            raise ValueError(f"Could not play {current_song['title']}: {str(e)}")
    
    def pause(self):
        """Pause the current song."""
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
    
    def stop(self):
        """Stop playback."""
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self._stop_visualizer.set()
    
    def next_song(self):
        """Play the next song in the playlist."""
        if not self.library.songs:
            return
        
        self.stop()
        self._stop_visualizer.clear()
        
        self.current_song_index = (self.current_song_index + 1) % len(self.library.songs)
        self.play()
    
    def previous_song(self):
        """Play the previous song in the playlist."""
        if not self.library.songs:
            return
        
        self.stop()
        self._stop_visualizer.clear()
        
        self.current_song_index = (self.current_song_index - 1) % len(self.library.songs)
        self.play()
    
    def set_volume(self, volume):
        """Set the playback volume.
        
        Args:
            volume: Float between 0.0 and 1.0
        """
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
    
    def get_current_song(self):
        """Get the currently selected song.
        
        Returns:
            Dictionary containing song metadata
        """
        if not self.library.songs:
            return None
        return self.library.songs[self.current_song_index]
    
    def get_playback_position(self):
        """Get the current playback position in seconds.
        
        Returns:
            Float representing seconds elapsed in the current song
        """
        if not self.playing:
            return 0
        
        return pygame.mixer.music.get_pos() / 1000  # Convert ms to seconds
    
    def get_song_length(self):
        """Get the length of the current song in seconds.
        
        Returns:
            Float representing the song length in seconds
        """
        if not self.library.songs:
            return 0
        
        current_song = self.library.songs[self.current_song_index]
        path = current_song['path']
        
        try:
            # Get song length based on file type
            if path.lower().endswith('.mp3'):
                audio = MP3(path)
                return audio.info.length
            elif path.lower().endswith('.flac'):
                audio = FLAC(path)
                return audio.info.length
            elif path.lower().endswith('.ogg'):
                audio = OggVorbis(path)
                return audio.info.length
            elif path.lower().endswith('.wav'):
                audio = WAVE(path)
                return audio.info.length
            else:
                return 0
        except Exception:
            return 0
    
    def is_playing(self):
        """Check if music is currently playing.
        
        Returns:
            Boolean indicating if music is playing
        """
        return self.playing and not self.paused and pygame.mixer.music.get_busy()
    
    def _start_visualizer(self):
        """Start the visualizer data generation thread."""
        self._stop_visualizer.clear()
        self._visualizer_thread = threading.Thread(target=self._generate_visualizer_data)
        self._visualizer_thread.daemon = True
        self._visualizer_thread.start()
    
    def _generate_visualizer_data(self):
        """Generate visualizer data based on the current audio.
        
        This is a simplified simulation since real-time audio analysis
        would require more complex audio processing.
        """
        while not self._stop_visualizer.is_set() and self.playing:
            if not pygame.mixer.music.get_busy():
                time.sleep(0.1)
                continue
            
            # Generate simulated frequency data
            # In a real implementation, this would analyze the audio buffer
            data = np.random.rand(64) * 0.3  # Base random noise
            
            # Add some peaks to make it look more like music
            peaks = np.random.randint(0, 64, 5)
            for peak in peaks:
                data[peak] = np.random.rand() * 0.7 + 0.3
            
            # Smooth transitions from previous frame
            self.visualizer_data = self.visualizer_data * 0.7 + data * 0.3
            
            time.sleep(0.05)  # Update at ~20fps
    
    def get_visualizer_data(self):
        """Get the current visualizer data.
        
        Returns:
            Numpy array of frequency data for visualization
        """
        return self.visualizer_data
    
    def cleanup(self):
        """Clean up resources."""
        self.stop()
        pygame.mixer.quit()
