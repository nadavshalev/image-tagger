import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
from datetime import datetime
from PIL import Image, ImageTk, ImageOps, ExifTags
import shutil

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, background="yellow", relief="solid", borderwidth=1, font=("tahoma", "8", "normal")
        )
        label.pack(ipadx=1, ipady=1)

    def hide_tooltip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class ImageTagger:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Tagger")

        # Initialize variables
        self.images = []
        self.current_index = 0
        self.liked_images = set()
        self.tagger_name = ""
        self.folder_path = ""

        # Create login screen
        self.create_login_screen()

        # Bind keyboard events
        self.root.bind('<Left>', lambda e: self.move_image(-1))
        self.root.bind('<Right>', lambda e: self.move_image(1))
        self.root.bind('1', lambda e: self.toggle_like())

    def create_login_screen(self):
        self.login_frame = tk.Frame(self.root, padx=20, pady=20)
        self.login_frame.pack(expand=True)

        tk.Label(self.login_frame, text="Who is tagging? (Enter your name)").pack()
        self.name_entry = tk.Entry(self.login_frame)
        self.name_entry.pack()
        self.name_entry.focus_set()

        select_button = tk.Button(self.login_frame, text="Select Folder", command=self.select_folder)
        select_button.pack(pady=10)

        # Bind Enter key to the Select Folder button
        self.root.bind('<Return>', lambda e: select_button.invoke())

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path and self.name_entry.get():
            self.tagger_name = self.name_entry.get()
            self.load_images()
            self.load_likes()
            self.login_frame.destroy()
            self.create_main_interface()


    def load_images(self):
        # Get all image files and sort by EXIF DateTimeOriginal
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif')
        self.images = []
        for file in os.listdir(self.folder_path):
            if file.lower().endswith(image_extensions):
                file_path = os.path.join(self.folder_path, file)
                try:
                    # Open the image and extract EXIF data
                    image = Image.open(file_path)
                    exif_data = image._getexif()
                    if exif_data:
                        # Get the DateTimeOriginal tag
                        for tag, value in ExifTags.TAGS.items():
                            if value == "DateTimeOriginal":
                                date_taken = exif_data.get(tag)
                                break
                        else:
                            date_taken = None
                    else:
                        date_taken = None
                except Exception:
                    date_taken = None

                # Fallback to file creation time if EXIF data is unavailable
                if date_taken:
                    # Convert EXIF date format (e.g., "2023:03:15 12:34:56") to a timestamp
                    date_taken = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S").timestamp()
                else:
                    date_taken = os.path.getctime(file_path)

                self.images.append((file_path, date_taken))

        # Sort by the extracted date
        self.images.sort(key=lambda x: x[1])
        self.images = [img[0] for img in self.images]

    def load_likes(self):
        likes_file = f"{self.tagger_name}_likes.json"
        if os.path.exists(likes_file):
            with open(likes_file, 'r') as f:
                self.liked_images = set(json.load(f))

    def save_likes(self):
        likes_file = f"{self.tagger_name}_likes.json"
        with open(likes_file, 'w') as f:
            json.dump(list(self.liked_images), f)


    def create_main_interface(self):
        # Main frame
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(expand=True, fill="both")

        # Title
        tk.Label(self.main_frame, text="Image Tagger", font=("Arial", 16, "bold")).pack(pady=10)

        # Image display
        self.image_label = tk.Label(self.main_frame, bg="gray", width=960, height=520)
        self.image_label.pack(pady=10)

        # Status bar
        self.status_label = tk.Label(self.main_frame, text="", font=("Arial", 10))
        self.status_label.pack(pady=5)

        # Progress bar
        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(
            self.main_frame, orient="horizontal", length=400, mode="determinate", variable=self.progress_var
        )
        self.progress.pack(pady=5)

        # Set the maximum value of the progress bar
        self.progress["maximum"] = len(self.images) - 1

        # Bind dragging event to update the image
        self.progress.bind("<ButtonRelease-1>", self.update_image_from_progress)

        # Navigation buttons (Next and Previous)
        nav_frame = tk.Frame(self.main_frame)
        nav_frame.pack(pady=10)

        prev_button = tk.Button(nav_frame, text="⏪ Previous", command=lambda: self.move_image(-1), font=("Arial", 10))
        prev_button.pack(side=tk.LEFT, padx=5)

        next_button = tk.Button(nav_frame, text="Next ⏩", command=lambda: self.move_image(1), font=("Arial", 10))
        next_button.pack(side=tk.LEFT, padx=5)

        # Like button (centered and larger)
        self.like_button = tk.Button(self.main_frame, text="🤍 Like", command=self.toggle_like, font=("Arial", 14, "bold"),
                                width=10, bg="lightgray")
        self.like_button.pack(pady=20)

        # Additional buttons (rarely used)
        additional_frame = tk.Frame(self.main_frame)
        additional_frame.pack(pady=10)

        jump_button = tk.Button(additional_frame, text="Jump to Last Liked", command=self.jump_to_last_liked,
                                font=("Arial", 10))
        jump_button.pack(side=tk.LEFT, padx=5)

        export_button = tk.Button(additional_frame, text="FINISH (Export Liked Images)", command=self.export_liked_images,
                                  font=("Arial", 10))
        export_button.pack(side=tk.LEFT, padx=5)

        # Add tooltips to buttons
        ToolTip(prev_button, "Shortcut: Left Arrow")
        ToolTip(next_button, "Shortcut: Right Arrow")
        ToolTip(self.like_button, "Shortcut: 1")
        ToolTip(export_button, "Export to a folder inside the current folder")

        # Show first image
        self.show_current_image()

    def show_current_image(self):
        if not self.images:
            return

        # Load and resize image
        image = Image.open(self.images[self.current_index])

        # Correct orientation using EXIF metadata
        image = ImageOps.exif_transpose(image)

        # Calculate resize dimensions maintaining aspect ratio
        display_size = (800, 600)
        image.thumbnail(display_size, Image.Resampling.LANCZOS)

        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo  # Keep a reference

        # Update progress bar
        self.progress["value"] = (self.current_index + 1) / len(self.images) * 100

        # Update status
        liked_status = "❤️ Liked" if self.images[self.current_index] in self.liked_images else "Not liked"
        self.status_label.config(
            text=f"Image {self.current_index + 1} of {len(self.images)}"
        )

        # Update Like button appearance
        if self.images[self.current_index] in self.liked_images:
            self.like_button.config(text="❤️ Liked", bg="lightgreen")
        else:
            self.like_button.config(text="🤍 Like", bg="lightgray")

    def move_image(self, delta):
        new_index = self.current_index + delta
        if 0 <= new_index < len(self.images):
            self.current_index = new_index
            self.show_current_image()

    def toggle_like(self):
        current_image = self.images[self.current_index]
        if current_image in self.liked_images:
            self.liked_images.remove(current_image)
        else:
            self.liked_images.add(current_image)
        self.save_likes()
        self.show_current_image()

    def update_image_from_progress(self, event):
        # Get the x-coordinate of the mouse relative to the progress bar
        progress_width = self.progress.winfo_width()
        click_x = event.x

        # Calculate the new progress value as a percentage
        new_value = max(0, min(click_x / progress_width, 1)) * (len(self.images) - 1)

        # Convert to an integer index
        new_index = int(new_value)

        if 0 <= new_index < len(self.images):
            self.current_index = new_index
            self.progress_var.set(new_index)
            self.show_current_image()
        else:
            print("New index is out of bounds")

    def jump_to_last_liked(self):
        # Find the last liked image after current position
        for i in range(len(self.images) - 1, -1, -1):
            if self.images[i] in self.liked_images:
                self.current_index = i
                self.show_current_image()
                break

    def export_liked_images(self):
        if not self.liked_images:
            messagebox.showinfo("Info", "No liked images to export!")
            return

        # Filter liked images to include only those in the current folder
        current_folder_liked_images = {
            image_path for image_path in self.liked_images if image_path.startswith(self.folder_path)
        }

        if not current_folder_liked_images:
            messagebox.showinfo("Info", "No liked images in the current folder to export!")
            return

        export_folder = os.path.join(self.folder_path, f"{self.tagger_name}_likes")
        os.makedirs(export_folder, exist_ok=True)

        for image_path in current_folder_liked_images:
            filename = os.path.basename(image_path)
            shutil.copy2(image_path, os.path.join(export_folder, filename))

        messagebox.showinfo("Success", f"Exported {len(current_folder_liked_images)} images to {export_folder}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageTagger(root)
    root.mainloop()
