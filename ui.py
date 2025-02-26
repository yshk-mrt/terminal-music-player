"""
UI Module
Handles the terminal user interface for the music player.
"""

import os
import sys
import time
import threading
import curses
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.live import Live

from visualizer import Visualizer

class PlayerUI:
    """Terminal UI class for the music player."""
    
    # Key mappings
    KEY_MAPPINGS = {
        ' ': 'play_pause',
        's': 'stop',
        'n': 'next',
        'p': 'previous',
        'q': 'quit',
        'v': 'change_visualizer',
        'up': 'volume_up',
        'down': 'volume_down',
        'left': 'rewind',
        'right': 'forward',
    }
    
    def __init__(self, player, library):
        """Initialize the UI.
        
        Args:
            player: MusicPlayer instance
            library: MusicLibrary instance
        """
        self.player = player
        self.library = library
        self.console = Console()
        self.visualizer = Visualizer()
        self.selected_index = 0
        self.scroll_offset = 0
        self.search_query = ""
        self.running = False
        self.update_interval = 0.1  # UI update interval in seconds
        
    def run(self):
        """Run the UI main loop."""
        self.running = True
        
        # Create the layout
        layout = self._create_layout()
        
        # Start the UI update loop
        with Live(layout, refresh_per_second=10, screen=True) as live:
            self.live = live
            
            # Main event loop
            while self.running:
                try:
                    # Update the layout
                    live.update(self._create_layout())
                    
                    # Handle keyboard input
                    self._handle_input()
                    
                    # Sleep to reduce CPU usage
                    time.sleep(self.update_interval)
                    
                except KeyboardInterrupt:
                    self.running = False
                except Exception as e:
                    self.console.print(f"[bold red]Error:[/bold red] {str(e)}")
                    self.running = False
        
        # Clean up resources
        self.player.cleanup()
        
    def _create_layout(self):
        """Create the UI layout.
        
        Returns:
            Rich layout object
        """
        # Create main layout
        layout = Layout()
        
        # Split into sections
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        # Split body into visualizer and playlist
        layout["body"].split_row(
            Layout(name="visualizer", ratio=2),
            Layout(name="playlist", ratio=1)
        )
        
        # Set content for each section
        layout["header"].update(self._create_header())
        layout["visualizer"].update(self._create_visualizer())
        layout["playlist"].update(self._create_playlist())
        layout["footer"].update(self._create_footer())
        
        return layout
    
    def _create_header(self):
        """Create the header section.
        
        Returns:
            Rich renderable object
        """
        # Get current song info
        current_song = self.player.get_current_song()
        
        if current_song:
            title = current_song.get('title', 'Unknown Title')
            artist = current_song.get('artist', 'Unknown Artist')
            album = current_song.get('album', 'Unknown Album')
            
            # Create progress bar
            position = self.player.get_playback_position()
            duration = self.player.get_song_length()
            
            progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=None),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("{task.completed:.0f}/{task.total:.0f}s"),
                expand=True
            )
            
            task_id = progress.add_task(
                f"[cyan]{title} - {artist}[/cyan]", 
                total=max(1, duration),
                completed=position
            )
            
            # Create header panel
            header_text = f"[bold cyan]♫ Now Playing:[/bold cyan] {title}\n"
            header_text += f"[cyan]Artist:[/cyan] {artist} [cyan]Album:[/cyan] {album}"
            
            header = Panel(
                progress,
                title=header_text,
                border_style="cyan"
            )
        else:
            # No song selected
            header = Panel(
                "[yellow]No song selected[/yellow]",
                title="[bold cyan]♫ Terminal Music Player[/bold cyan]",
                border_style="cyan"
            )
        
        return header
    
    def _create_visualizer(self):
        """Create the visualizer section.
        
        Returns:
            Rich renderable object
        """
        # Get visualizer data
        data = self.player.get_visualizer_data()
        is_playing = self.player.is_playing()
        
        # Render visualizer
        vis_lines = self.visualizer.render(data, is_playing)
        
        # Create visualizer panel
        vis_panel = Panel(
            "\n".join([str(line) for line in vis_lines]),
            title=f"[bold cyan]Visualizer ({self.visualizer.mode})[/bold cyan]",
            border_style="cyan"
        )
        
        return vis_panel
    
    def _create_playlist(self):
        """Create the playlist section.
        
        Returns:
            Rich renderable object
        """
        # Create table for playlist
        table = Table(box=None, expand=True, show_header=False)
        table.add_column("Song")
        
        # Get visible height for playlist
        visible_rows = 10  # Approximate number of visible rows
        
        # Adjust scroll offset if needed
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_rows:
            self.scroll_offset = self.selected_index - visible_rows + 1
        
        # Add songs to the playlist
        songs = self.library.songs
        for i in range(self.scroll_offset, min(len(songs), self.scroll_offset + visible_rows)):
            song = songs[i]
            title = song.get('title', 'Unknown Title')
            artist = song.get('artist', 'Unknown Artist')
            
            # Format the song entry
            if i == self.selected_index:
                # Selected song
                text = Text(f"> {title} - {artist}")
                text.stylize("bold cyan")
            else:
                # Regular song
                text = Text(f"  {title} - {artist}")
            
            table.add_row(text)
        
        # Create playlist panel
        playlist_panel = Panel(
            table,
            title=f"[bold cyan]Playlist ({len(songs)} songs)[/bold cyan]",
            border_style="cyan"
        )
        
        return playlist_panel
    
    def _create_footer(self):
        """Create the footer section.
        
        Returns:
            Rich renderable object
        """
        # Create footer text with controls
        controls = [
            ("[Space]", "Play/Pause"),
            ("[S]", "Stop"),
            ("[N]", "Next"),
            ("[P]", "Previous"),
            ("[V]", "Visualizer"),
            ("[↑/↓]", "Volume"),
            ("[←/→]", "Seek"),
            ("[Q]", "Quit")
        ]
        
        # Format controls
        control_text = Text()
        for i, (key, action) in enumerate(controls):
            if i > 0:
                control_text.append("  ")
            control_text.append(key, style="bold cyan")
            control_text.append(f" {action}")
        
        # Create footer panel
        footer = Panel(
            control_text,
            border_style="cyan"
        )
        
        return footer
    
    def _handle_input(self):
        """Handle keyboard input."""
        # Check if a key is pressed
        key = self._get_key_press()
        if not key:
            return
        
        # Map key to action
        action = self.KEY_MAPPINGS.get(key)
        if not action:
            return
        
        # Execute action
        if action == 'play_pause':
            if self.player.playing and not self.player.paused:
                self.player.pause()
            else:
                self.player.play()
        
        elif action == 'stop':
            self.player.stop()
        
        elif action == 'next':
            self.player.next_song()
            self.selected_index = self.player.current_song_index
        
        elif action == 'previous':
            self.player.previous_song()
            self.selected_index = self.player.current_song_index
        
        elif action == 'quit':
            self.running = False
        
        elif action == 'change_visualizer':
            # Cycle through visualizer modes
            modes = ["bars", "wave", "spectrum"]
            current_idx = modes.index(self.visualizer.mode)
            next_idx = (current_idx + 1) % len(modes)
            self.visualizer.set_mode(modes[next_idx])
        
        elif action == 'volume_up':
            self.player.set_volume(self.player.volume + 0.05)
        
        elif action == 'volume_down':
            self.player.set_volume(self.player.volume - 0.05)
        
        elif action == 'rewind':
            # Not implemented (would require more complex audio control)
            pass
        
        elif action == 'forward':
            # Not implemented (would require more complex audio control)
            pass
    
    def _get_key_press(self):
        """Get a key press from the terminal.
        
        Returns:
            String representing the key pressed, or None if no key was pressed
        """
        # This is a simplified implementation that works with the Live display
        # In a real application, you would use a proper terminal input library
        
        # Check if a key is available
        import sys
        import select
        import termios
        import tty
        
        # Set terminal to raw mode
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno(), termios.TCSANOW)
            
            # Check if input is available
            if select.select([sys.stdin], [], [], 0)[0]:
                # Read a key
                key = sys.stdin.read(1)
                
                # Handle special keys (arrow keys, etc.)
                if key == '\x1b':  # Escape sequence
                    # Read the next two characters
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        seq1 = sys.stdin.read(1)
                        if seq1 == '[' and select.select([sys.stdin], [], [], 0.1)[0]:
                            seq2 = sys.stdin.read(1)
                            
                            # Map arrow keys
                            if seq2 == 'A':
                                return 'up'
                            elif seq2 == 'B':
                                return 'down'
                            elif seq2 == 'C':
                                return 'right'
                            elif seq2 == 'D':
                                return 'left'
                
                return key
            
            return None
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
