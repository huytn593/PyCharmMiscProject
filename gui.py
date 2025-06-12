import tkinter as tk
from tkinter import ttk, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
from script import add_track, STORAGE_BASE, TRACKS_PATH, COVER_PATH, get_filename_without_extension
from datetime import datetime, UTC
import shutil
from PIL import Image, ImageTk

class MusicUploaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Track Uploader")
        self.root.geometry("1000x800")  # Increased window size
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('DropZone.TLabel', 
                           font=('Helvetica', 12),
                           padding=20,
                           background='#f0f0f0',
                           foreground='#666666')
        
        # Variables
        self.title_var = tk.StringVar()
        self.genres_var = tk.StringVar()
        self.is_public_var = tk.BooleanVar(value=True)
        
        # File paths
        self.mp3_path = None
        self.cover_path = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, 
                              text="Music Track Uploader", 
                              font=('Helvetica', 24, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Basic Info Section
        info_frame = ttk.LabelFrame(main_frame, text="Track Information", padding="20")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        info_frame.columnconfigure(1, weight=1)
        
        # Title
        ttk.Label(info_frame, text="Title:", font=('Helvetica', 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(info_frame, textvariable=self.title_var, width=40, font=('Helvetica', 12)).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Genres
        ttk.Label(info_frame, text="Genres:", font=('Helvetica', 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(info_frame, textvariable=self.genres_var, width=40, font=('Helvetica', 12)).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Label(info_frame, text="(comma-separated)", font=('Helvetica', 10)).grid(row=1, column=2, sticky=tk.W)
        
        # Public/Private
        ttk.Checkbutton(info_frame, text="Make Public", variable=self.is_public_var, font=('Helvetica', 12)).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # File Upload Section
        files_frame = ttk.LabelFrame(main_frame, text="File Upload", padding="20")
        files_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        files_frame.columnconfigure(0, weight=1)
        
        # MP3 File
        mp3_frame = ttk.Frame(files_frame)
        mp3_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        mp3_frame.columnconfigure(1, weight=1)
        
        ttk.Label(mp3_frame, text="MP3 File:", font=('Helvetica', 12)).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Create a frame for the drop zone
        mp3_drop_frame = ttk.Frame(mp3_frame, style='DropZone.TFrame')
        mp3_drop_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        mp3_drop_frame.columnconfigure(0, weight=1)
        
        self.mp3_label = ttk.Label(mp3_drop_frame, 
                                 text="Drop MP3 file here\nor click to browse",
                                 style='DropZone.TLabel',
                                 anchor='center')
        self.mp3_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.mp3_label.bind('<Button-1>', lambda e: self.browse_file('mp3'))
        self.mp3_label.drop_target_register(DND_FILES)
        self.mp3_label.dnd_bind('<<Drop>>', lambda e: self.handle_drop(e, 'mp3'))
        
        # Cover Image
        cover_frame = ttk.Frame(files_frame)
        cover_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        cover_frame.columnconfigure(1, weight=1)
        
        ttk.Label(cover_frame, text="Cover Image:", font=('Helvetica', 12)).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Create a frame for the drop zone
        cover_drop_frame = ttk.Frame(cover_frame, style='DropZone.TFrame')
        cover_drop_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        cover_drop_frame.columnconfigure(0, weight=1)
        
        self.cover_label = ttk.Label(cover_drop_frame, 
                                   text="Drop image file here\nor click to browse",
                                   style='DropZone.TLabel',
                                   anchor='center')
        self.cover_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.cover_label.bind('<Button-1>', lambda e: self.browse_file('cover'))
        self.cover_label.drop_target_register(DND_FILES)
        self.cover_label.dnd_bind('<<Drop>>', lambda e: self.handle_drop(e, 'cover'))
        
        # Upload Button
        upload_button = ttk.Button(main_frame, 
                                 text="Upload Track", 
                                 command=self.upload_track,
                                 style='Accent.TButton')
        upload_button.grid(row=3, column=0, pady=20)
        
        # Status Label
        self.status_label = ttk.Label(main_frame, 
                                    text="",
                                    font=('Helvetica', 12))
        self.status_label.grid(row=4, column=0)
        
        # Configure custom styles
        self.style.configure('Accent.TButton', 
                           font=('Helvetica', 12, 'bold'),
                           padding=10)
        
    def browse_file(self, file_type):
        filetypes = {
            'mp3': [('MP3 files', '*.mp3')],
            'cover': [('Image files', '*.jpg *.jpeg *.png')]
        }
        
        filename = filedialog.askopenfilename(filetypes=filetypes[file_type])
        if filename:
            self.handle_file_selection(filename, file_type)
    
    def handle_drop(self, event, file_type):
        file_path = event.data
        # Remove curly braces if present (Windows path format)
        file_path = file_path.strip('{}')
        self.handle_file_selection(file_path, file_type)
    
    def handle_file_selection(self, file_path, file_type):
        if file_type == 'mp3':
            self.mp3_path = file_path
            self.mp3_label.config(text=f"Selected: {os.path.basename(file_path)}")
            # Auto-fill title if empty
            if not self.title_var.get():
                self.title_var.set(get_filename_without_extension(os.path.basename(file_path)))
        elif file_type == 'cover':
            self.cover_path = file_path
            self.cover_label.config(text=f"Selected: {os.path.basename(file_path)}")
    
    def copy_file_to_storage(self, source_path, target_dir):
        if not source_path:
            return None
            
        filename = os.path.basename(source_path)
        target_path = os.path.join(target_dir, filename).replace("\\", "/")
        
        # Create directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Copy file
        shutil.copy2(source_path, target_path)
        return filename
    
    def upload_track(self):
        if not self.mp3_path:
            self.status_label.config(text="Error: MP3 file is required!")
            return
            
        try:
            # Copy files to storage
            mp3_filename = self.copy_file_to_storage(self.mp3_path, TRACKS_PATH)  # Copy to storage/tracks
            cover_filename = self.copy_file_to_storage(self.cover_path, COVER_PATH)  # Copy to storage/cover_image
            
            # Get genres
            genres = [g.strip() for g in self.genres_var.get().split(',')] if self.genres_var.get() else None
            
            # Add track to database
            success = add_track(
                title=self.title_var.get(),
                filename=mp3_filename,
                genres=genres,
                cover_image=cover_filename,
                is_public=self.is_public_var.get()
            )
            
            if success:
                self.status_label.config(text="Track uploaded successfully!")
                self.clear_form()
            else:
                self.status_label.config(text="Error uploading track!")
                
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
    
    def clear_form(self):
        self.title_var.set("")
        self.genres_var.set("")
        self.is_public_var.set(True)
        self.mp3_path = None
        self.cover_path = None
        self.mp3_label.config(text="Drop MP3 file here\nor click to browse")
        self.cover_label.config(text="Drop image file here\nor click to browse")

def main():
    root = TkinterDnD.Tk()
    app = MusicUploaderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 