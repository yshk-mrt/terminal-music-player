"""
Visualizer Module
Handles audio visualization in the terminal.
"""

import math
import numpy as np
from rich.console import Console
from rich.text import Text

class Visualizer:
    """Audio visualizer class for terminal display."""
    
    # Color gradients for visualizer
    GRADIENT_COLORS = [
        "bright_blue",
        "blue",
        "cyan",
        "bright_cyan",
        "green",
        "bright_green",
        "yellow",
        "bright_yellow",
        "red",
        "bright_red",
        "magenta",
        "bright_magenta"
    ]
    
    def __init__(self, width=60, height=8):
        """Initialize the visualizer.
        
        Args:
            width: Width of the visualizer in characters
            height: Height of the visualizer in characters
        """
        self.width = width
        self.height = height
        self.mode = "bars"  # Default visualization mode
        self.console = Console()
        
    def set_mode(self, mode):
        """Set the visualization mode.
        
        Args:
            mode: Visualization mode ("bars", "wave", "spectrum")
        """
        if mode in ["bars", "wave", "spectrum"]:
            self.mode = mode
    
    def render(self, data, is_playing=True):
        """Render the audio visualization.
        
        Args:
            data: Numpy array of audio frequency data
            is_playing: Boolean indicating if music is playing
        
        Returns:
            List of rich.Text objects representing the visualization
        """
        if not is_playing:
            return self._render_idle()
        
        if self.mode == "bars":
            return self._render_bars(data)
        elif self.mode == "wave":
            return self._render_wave(data)
        elif self.mode == "spectrum":
            return self._render_spectrum(data)
        else:
            return self._render_bars(data)  # Default to bars
    
    def _render_idle(self):
        """Render idle visualization when no music is playing.
        
        Returns:
            List of rich.Text objects representing the idle visualization
        """
        lines = []
        
        # Create a simple idle animation
        mid = self.height // 2
        for i in range(self.height):
            if i == mid:
                text = Text("♫ Press SPACE to play music ♫".center(self.width))
                text.stylize("bright_cyan")
            else:
                text = Text(" " * self.width)
            lines.append(text)
        
        return lines
    
    def _render_bars(self, data):
        """Render bar visualization.
        
        Args:
            data: Numpy array of audio frequency data
        
        Returns:
            List of rich.Text objects representing the bar visualization
        """
        # Number of bars to display
        num_bars = min(len(data), self.width // 2)
        
        # Resample data to match the number of bars
        if len(data) != num_bars:
            indices = np.linspace(0, len(data) - 1, num_bars).astype(int)
            data = data[indices]
        
        # Scale data to fit the height
        scaled_data = data * self.height
        
        # Create the visualization
        lines = []
        for y in range(self.height, 0, -1):
            line = Text("")
            for x in range(num_bars):
                bar_height = scaled_data[x]
                
                if bar_height >= y:
                    # Calculate color based on bar height
                    color_idx = min(int(bar_height / self.height * len(self.GRADIENT_COLORS)), 
                                   len(self.GRADIENT_COLORS) - 1)
                    color = self.GRADIENT_COLORS[color_idx]
                    
                    # Add the bar segment with color
                    line.append("▮▮", style=color)
                else:
                    # Empty space
                    line.append("  ")
            
            lines.append(line)
        
        return lines
    
    def _render_wave(self, data):
        """Render wave visualization.
        
        Args:
            data: Numpy array of audio frequency data
        
        Returns:
            List of rich.Text objects representing the wave visualization
        """
        # Number of points in the wave
        num_points = min(len(data), self.width)
        
        # Resample data to match the number of points
        if len(data) != num_points:
            indices = np.linspace(0, len(data) - 1, num_points).astype(int)
            data = data[indices]
        
        # Scale data to fit the height and center it
        mid = self.height // 2
        scaled_data = data * (self.height // 2)
        
        # Create a 2D grid for the visualization
        grid = [[" " for _ in range(num_points)] for _ in range(self.height)]
        
        # Plot the wave
        for x in range(num_points):
            # Calculate y position (centered)
            y = mid - int(scaled_data[x])
            y = max(0, min(self.height - 1, y))
            
            # Calculate color based on distance from center
            color_idx = min(int(abs(y - mid) / (self.height // 2) * len(self.GRADIENT_COLORS)), 
                           len(self.GRADIENT_COLORS) - 1)
            color = self.GRADIENT_COLORS[color_idx]
            
            # Place the wave point
            grid[y][x] = color
        
        # Create the visualization
        lines = []
        for y in range(self.height):
            line = Text("")
            for x in range(num_points):
                if grid[y][x] != " ":
                    line.append("●", style=grid[y][x])
                else:
                    line.append(" ")
            
            lines.append(line)
        
        return lines
    
    def _render_spectrum(self, data):
        """Render spectrum visualization.
        
        Args:
            data: Numpy array of audio frequency data
        
        Returns:
            List of rich.Text objects representing the spectrum visualization
        """
        # Number of segments in the spectrum
        num_segments = min(len(data), self.width)
        
        # Resample data to match the number of segments
        if len(data) != num_segments:
            indices = np.linspace(0, len(data) - 1, num_segments).astype(int)
            data = data[indices]
        
        # Apply logarithmic scaling to emphasize lower frequencies
        log_data = np.log10(data + 1) * 1.5
        
        # Scale data to fit the height
        scaled_data = log_data * self.height
        
        # Create the visualization
        lines = []
        for y in range(self.height, 0, -1):
            line = Text("")
            for x in range(num_segments):
                intensity = scaled_data[x]
                
                if intensity >= y:
                    # Calculate color based on frequency (x position)
                    color_idx = min(int(x / num_segments * len(self.GRADIENT_COLORS)), 
                                   len(self.GRADIENT_COLORS) - 1)
                    color = self.GRADIENT_COLORS[color_idx]
                    
                    # Add the spectrum segment with color
                    line.append("█", style=color)
                else:
                    # Empty space
                    line.append(" ")
            
            lines.append(line)
        
        return lines
