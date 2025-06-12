import os
from pymongo import MongoClient
from datetime import datetime, UTC
import shutil
from bson import ObjectId
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# Initialize rich console
console = Console()

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['music_db']
tracks_collection = db['tracks']

# Storage paths
STORAGE_BASE = "storage"
TRACKS_PATH = os.path.join(STORAGE_BASE, "tracks").replace("\\", "/")
COVER_PATH = os.path.join(STORAGE_BASE, "cover_image").replace("\\", "/")

def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(TRACKS_PATH, exist_ok=True)
    os.makedirs(COVER_PATH, exist_ok=True)

def get_filename_without_extension(filename):
    """Extract filename without extension"""
    return os.path.splitext(filename)[0]

def add_track(title, filename, genres=None, cover_image=None, is_public=True):
    """
    Add a new track to the database
    
    Args:
        title (str): Track title
        filename (str): MP3 filename
        genres (list, optional): List of genres
        cover_image (str, optional): Cover image filename
        is_public (bool): Whether the track is public
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create track document
        track_doc = {
            "title": title,
            "filename": filename,  # Store only filename in MongoDB
            "genres": genres,
            "cover_image": cover_image,  # Store only filename in MongoDB
            "like_count": 0,
            "play_count": 0,
            "is_public": is_public,
            "is_approved": False,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC)
        }
        
        # Insert into MongoDB
        result = tracks_collection.insert_one(track_doc)
        return result.inserted_id is not None
        
    except Exception as e:
        console.print(f"[red]Error adding track: {str(e)}[/red]")
        return False

def display_track_info(track_info):
    """Display track information in a nice table format"""
    table = Table(title="Track Information", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    for key, value in track_info.items():
        if value is not None:
            if isinstance(value, list):
                value = ", ".join(value)
            table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)

def main():
    console.clear()
    console.print(Panel.fit(
        "[bold blue]🎵 Music Track Upload System[/bold blue]",
        border_style="blue"
    ))

    # Get track information with rich prompts
    track_info = {
        "filename": Prompt.ask("\n[bold cyan]Audio Filename[/bold cyan]", default="example.mp3"),
        "genres": [g.strip() for g in Prompt.ask("[bold cyan]Genres[/bold cyan] (comma-separated, optional)").split(",")] if Prompt.ask("[bold cyan]Genres[/bold cyan] (comma-separated, optional)") else None,
        "cover_image": Prompt.ask("[bold cyan]Cover Image Filename[/bold cyan] (optional)") or None,
        "is_public": Confirm.ask("[bold cyan]Make track public?[/bold cyan]", default=True)
    }

    # Display entered information
    console.print("\n[bold yellow]Review Track Information:[/bold yellow]")
    display_track_info(track_info)

    # Confirm before proceeding
    if not Confirm.ask("\n[bold]Proceed with upload?[/bold]"):
        console.print("[yellow]Upload cancelled.[/yellow]")
        return

    # Add track to MongoDB
    success = add_track(
        title=track_info["filename"],
        filename=track_info["filename"],
        genres=track_info["genres"],
        cover_image=track_info["cover_image"],
        is_public=track_info["is_public"]
    )

    if success:
        console.print("\n[bold green]✅ Track added successfully![/bold green]")
        console.print(f"[cyan]Audio file path:[/cyan] {os.path.join(TRACKS_PATH, track_info['filename'])}")
        if track_info['cover_image']:
            console.print(f"[cyan]Cover image path:[/cyan] {os.path.join(COVER_PATH, track_info['cover_image'])}")
    else:
        console.print("\n[bold red]❌ Failed to add track.[/bold red]")

if __name__ == "__main__":
    main() 