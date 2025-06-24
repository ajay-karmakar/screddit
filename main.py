import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
import threading
from PIL import Image, ImageTk
import sys
from reddit_image_scraper import scrape_subreddit_images
from reddit_video_scraper import scrape_subreddit_videos
from third_party_gif import scrape_gif_videos

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue")

class screddit(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Screddit")
        self.geometry("600x650")
        self.minsize(500, 600)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        
        # Initialize variables
        self.subreddit_var = ctk.StringVar()
        self.sort_var = ctk.StringVar(value="hot")
        self.media_type_var = ctk.StringVar(value="images")
        self.download_folder = ctk.StringVar()
        self.use_custom_folder = ctk.BooleanVar(value=False)
        self.limit_var = ctk.StringVar(value="50")
        
        # Set default download folder to parent downloads directory
        self.parent_download_dir = os.path.join(os.getcwd(), "reddit_downloads")
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # App title
        self.title_label = ctk.CTkLabel(self.main_frame, text="Reddit Media Scraper", 
                                        font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)
        
        # Subreddit input
        self.subreddit_frame = ctk.CTkFrame(self.main_frame)
        self.subreddit_frame.pack(fill="x", pady=10, padx=20)
        
        self.subreddit_label = ctk.CTkLabel(self.subreddit_frame, text="Subreddit:", 
                                           font=ctk.CTkFont(size=14))
        self.subreddit_label.pack(side="left", padx=(0, 10))
        
        self.subreddit_entry = ctk.CTkEntry(self.subreddit_frame, textvariable=self.subreddit_var,
                                           placeholder_text="Enter subreddit name (without r/)",
                                           width=300)
        self.subreddit_entry.pack(side="left", fill="x", expand=True)
        
        # Sort options
        self.sort_frame = ctk.CTkFrame(self.main_frame)
        self.sort_frame.pack(fill="x", pady=10, padx=20)
        
        self.sort_label = ctk.CTkLabel(self.sort_frame, text="Sort by:", 
                                      font=ctk.CTkFont(size=14))
        self.sort_label.pack(side="left", padx=(0, 10))
        
        sort_options = ["hot", "new", "top", "best", "rising"]
        self.sort_option_menu = ctk.CTkOptionMenu(self.sort_frame, values=sort_options,
                                                variable=self.sort_var)
        self.sort_option_menu.pack(side="left", fill="x", expand=True)
          # Media type selection
        self.media_frame = ctk.CTkFrame(self.main_frame)
        self.media_frame.pack(fill="x", pady=10, padx=20)
        
        self.media_label = ctk.CTkLabel(self.media_frame, text="Media Type:", 
                                       font=ctk.CTkFont(size=14))
        self.media_label.pack(side="left", padx=(0, 10))
        
        self.image_radio = ctk.CTkRadioButton(self.media_frame, text="Images", 
                                             variable=self.media_type_var, value="images")
        self.image_radio.pack(side="left", padx=20)
        
        self.video_radio = ctk.CTkRadioButton(self.media_frame, text="Videos", 
                                             variable=self.media_type_var, value="videos")
        self.video_radio.pack(side="left", padx=20)
        
        self.gif_radio = ctk.CTkRadioButton(self.media_frame, text="Third-party gifs", 
                                             variable=self.media_type_var, value="Third-party gifs")
        self.gif_radio.pack(side="left", padx=20)
        
        # Limit input
        self.limit_frame = ctk.CTkFrame(self.main_frame)
        self.limit_frame.pack(fill="x", pady=10, padx=20)
        
        self.limit_label = ctk.CTkLabel(self.limit_frame, text="Download Limit:", 
                                       font=ctk.CTkFont(size=14))
        self.limit_label.pack(side="left", padx=(0, 10))
        
        self.limit_entry = ctk.CTkEntry(self.limit_frame, textvariable=self.limit_var, width=100)
        self.limit_entry.pack(side="left", padx=10)
        
        # Folder selection
        self.folder_frame = ctk.CTkFrame(self.main_frame)
        self.folder_frame.pack(fill="x", pady=10, padx=20)
        
        self.folder_label = ctk.CTkLabel(self.folder_frame, text="Save to:", 
                                        font=ctk.CTkFont(size=14))
        self.folder_label.pack(side="left", padx=(0, 10))
        
        self.custom_folder_checkbox = ctk.CTkCheckBox(self.folder_frame, text="Use custom folder", 
                                                   variable=self.use_custom_folder, 
                                                   command=self.toggle_custom_folder)
        self.custom_folder_checkbox.pack(side="left", padx=10)
        
        self.folder_entry = ctk.CTkEntry(self.folder_frame, textvariable=self.download_folder, 
                                        width=300, state="disabled")
        self.folder_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
        
        self.browse_button = ctk.CTkButton(self.folder_frame, text="Browse", 
                                         command=self.browse_folder, width=100, state="disabled")
        self.browse_button.pack(side="right")
        
        # Download button
        self.download_button = ctk.CTkButton(self.main_frame, text="Start Download", 
                                          command=self.start_download,
                                          font=ctk.CTkFont(size=16), height=40)
        self.download_button.pack(pady=20)
        
        # Log area
        self.log_frame = ctk.CTkFrame(self.main_frame)
        self.log_frame.pack(fill="both", expand=True, pady=10, padx=20)
        
        self.log_label = ctk.CTkLabel(self.log_frame, text="Activity Log:", 
                                     font=ctk.CTkFont(size=14))
        self.log_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # Create a text box for logs
        self.log_text = ctk.CTkTextbox(self.log_frame, wrap="word", height=200)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_text.configure(state="disabled")

        # Status bar
        self.status_var = ctk.StringVar(value="Ready")
        self.status_bar = ctk.CTkLabel(self, textvariable=self.status_var, 
                                     font=ctk.CTkFont(size=12))
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)
        
        # Bind subreddit entry changes to update folder name
        self.subreddit_var.trace_add("write", self.on_subreddit_change)
        
    def log_message(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        self.update_idletasks()
        
    def update_status(self, message):
        self.status_var.set(message)
        self.update_idletasks()
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_folder.set(folder)
            
    def toggle_custom_folder(self):
        if self.use_custom_folder.get():
            self.folder_entry.configure(state="normal")
            self.browse_button.configure(state="normal")
            if not self.download_folder.get():
                self.download_folder.set(self.parent_download_dir)
        else:
            self.folder_entry.configure(state="disabled")
            self.browse_button.configure(state="disabled")
            self.download_folder.set("")
            
    def on_subreddit_change(self, *args):
        pass
            
    def validate_inputs(self):
        if not self.subreddit_var.get().strip():
            self.log_message("Error: Please enter a subreddit name")
            return False
            
        try:
            limit = int(self.limit_var.get())
            if limit <= 0:
                self.log_message("Error: Download limit must be a positive number")
                return False
        except ValueError:
            self.log_message("Error: Download limit must be a number")
            return False
            
        return True
            
    def start_download(self):
        if not self.validate_inputs():
            return
            
        # Disable the download button during download
        self.download_button.configure(state="disabled")
        self.update_status("Downloading...")
        
        # Create output directory using subreddit name if custom folder isn't specified
        subreddit = self.subreddit_var.get().strip()
        
        if self.use_custom_folder.get():
            # User specified a custom folder
            base_dir = self.download_folder.get()
        else:
            # Use subreddit name as the folder name inside parent directory
            base_dir = os.path.join(self.parent_download_dir, subreddit)
            self.log_message(f"Using subreddit name for folder: {base_dir}")
          # Add media type subfolder
        media_type = self.media_type_var.get()
        if media_type == "images":
            output_dir = os.path.join(base_dir, "images")
        elif media_type == "videos":
            output_dir = os.path.join(base_dir, "videos")
        else:
            output_dir = os.path.join(base_dir, "redgif_videos")
            
        # Create the directory
        os.makedirs(output_dir, exist_ok=True)
            
        # Start download in a separate thread
        download_thread = threading.Thread(target=self.download_media, args=(output_dir,))
        download_thread.daemon = True
        download_thread.start()
        
    def download_media(self, output_dir):
        try:
            subreddit = self.subreddit_var.get().strip()
            sort_type = self.sort_var.get()
            media_type = self.media_type_var.get()
            limit = int(self.limit_var.get())
            
            self.log_message(f"Starting download from r/{subreddit} ({sort_type})")
            self.log_message(f"Saving to: {output_dir}")
            
            class StdoutRedirector:
                def __init__(self, app):
                    self.app = app
                    
                def write(self, text):
                    if text.strip():  # Only log non-empty lines
                        self.app.log_message(text.strip())
                    
                def flush(self):
                    pass
                    
            original_stdout = sys.stdout
            sys.stdout = StdoutRedirector(self)
              # Call the appropriate scraper function
            if media_type == "images":                scrape_subreddit_images(subreddit, sort_type=sort_type, 
                                        output_dir=output_dir, limit=limit)
            elif media_type == "videos":
                scrape_subreddit_videos(subreddit, sort_type=sort_type, 
                                        output_dir=output_dir, limit=limit)
            else:
                scrape_gif_videos(subreddit, sort_type=sort_type, 
                                   output_dir=output_dir, limit=limit)
                
            # Restore stdout
            sys.stdout = original_stdout
            
            self.log_message(f"Download completed!")
            self.update_status("Download completed")
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            self.update_status("Error occurred")
        finally:
            # Re-enable the download button
            self.download_button.configure(state="normal")


if __name__ == "__main__":
    app = screddit()
    app.mainloop()