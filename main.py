#!/usr/bin/env python3
"""
Terminal Music Player
A visually appealing music player for the macOS terminal with song selection,
playback controls, and audio visualization.
"""

import os
import sys
import time
import argparse
from rich.console import Console

from player import MusicPlayer
from ui import PlayerUI
from library import MusicLibrary

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Terminal Music Player')
    parser.add_argument(
        '-d', '--directory',
        default=os.path.expanduser('~/Music'),
        help='Directory containing music files (default: ~/Music)'
    )
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Initialize console
    console = Console()
    
    # Display welcome message
    console.print("[bold cyan]Terminal Music Player[/bold cyan]", justify="center")
    console.print("[cyan]Starting up...[/cyan]", justify="center")
    
    try:
        # Initialize music library
        library = MusicLibrary(args.directory)
        
        # Initialize music player
        player = MusicPlayer(library)
        
        # Initialize and run the UI
        ui = PlayerUI(player, library)
        ui.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Exiting Terminal Music Player...[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
