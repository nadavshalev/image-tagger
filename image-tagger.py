import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
from datetime import datetime
from PIL import Image, ImageTk, ImageOps, ExifTags
import shutil


class ToolTip:
    """Class to create and manage tooltips for widgets."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Display the tooltip when the mouse enters the widget."""
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
        """Hide the tooltip when the mouse leaves the widget."""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class ImageTagger:
    """Main class for the Image Tagger application."""

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
        self.bind_keyboard_events()

    def bind_keyboard_events(self):
        """Bind keyboard shortcuts for navigation and liking images."""
        self.root.bind('<Left>', lambda e: self.move_image(-1))
        self.root.bind('<Right>', lambda e: self.move_image(1))
        self.root.bind('1', lambda e: self.toggle_like())

    def create_login_screen(self):
        """Create the login screen for the user to enter their name and select a folder."""
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
        """Handle folder selection and proceed to load images."""
        self.folder_path = filedialog.askdirectory()
        if self.folder_path and self.name_entry.get():
            self.tagger_name = self.name_entry.get()
            self.load_images()
            self.load_likes()
            self.login_frame.destroy()
            self.create_main_interface()

    def load_images(self):
        """Load and sort images from the selected folder."""
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif')
        self.images = []

        for file in os.listdir(self.folder_path):
            if file.lower().endswith(image_extensions):
                file_path = os.path.join(self.folder_path, file)
                date_taken = self.get_image_date(file_path)
                self.images.append((file_path, date_taken))

        # Sort images by date
        self.images.sort(key=lambda x: x[1])
        self.images = [img[0] for img in self.images]

    def get_image_date(self, file_path):
        """Extract the date the image was taken or fallback to file creation time."""
        try:
            image = Image.open(file_path)
            exif_data = image._getexif()
            if exif_data:
                for tag, value in ExifTags.TAGS.items():
                    if value == "DateTimeOriginal":
                        date_taken = exif_data.get(tag)
                        break
                else:
                    date_taken = None
            else:
                date_taken = None

            if date_taken:
                return datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S").timestamp()
        except Exception:
            pass

        return os.path.getctime(file_path)

    def load_likes(self):
        """Load liked images from a JSON file."""
        likes_file = f"{self.tagger_name}_likes.json"
        if os.path.exists(likes_file):
            with open(likes_file, 'r') as f:
                self.liked_images = set(json.load(f))

    def save_likes(self):
        """Save liked images to a JSON file."""
        likes_file = f"{self.tagger_name}_likes.json"
        with open(likes_file, 'w') as f:
            json.dump(list(self.liked_images), f)

    def create_main_interface(self):
        """Create the main interface for tagging images."""
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(expand=True, fill="both")

        self.create_title()
        self.create_image_display()
        self.create_status_bar()
        self.create_progress_bar()
        self.create_navigation_buttons()
        self.create_like_button()
        self.create_additional_buttons()

        # Show the first image
        self.show_current_image()

    def create_title(self):
        """Create the title label."""
        tk.Label(self.main_frame, text="Image Tagger", font=("Arial", 16, "bold")).pack(pady=10)

    def create_image_display(self):
        """Create the image display area."""
        self.image_label = tk.Label(self.main_frame, bg="gray", width=960, height=520)
        self.image_label.pack(pady=10)

    def create_status_bar(self):
        """Create the status bar to display image information."""
        self.status_label = tk.Label(self.main_frame, text="", font=("Arial", 10))
        self.status_label.pack(pady=5)

    def create_progress_bar(self):
        """Create the progress bar for image navigation."""
        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(
            self.main_frame, orient="horizontal", length=400, mode="determinate", variable=self.progress_var
        )
        self.progress.pack(pady=5)
        self.progress["maximum"] = len(self.images) - 1
        self.progress.bind("<ButtonRelease-1>", self.update_image_from_progress)

    def create_navigation_buttons(self):
        """Create navigation buttons for moving between images."""
        nav_frame = tk.Frame(self.main_frame)
        nav_frame.pack(pady=10)

        prev_button = tk.Button(nav_frame, text="⏪ Previous", command=lambda: self.move_image(-1), font=("Arial", 10))
        prev_button.pack(side=tk.LEFT, padx=5)

        next_button = tk.Button(nav_frame, text="Next ⏩", command=lambda: self.move_image(1), font=("Arial", 10))
        next_button.pack(side=tk.LEFT, padx=5)

        ToolTip(prev_button, "Shortcut: Left Arrow")
        ToolTip(next_button, "Shortcut: Right Arrow")

    def create_like_button(self):
        """Create the like button."""
        self.like_button = tk.Button(
            self.main_frame, text="🤍 Like", command=self.toggle_like, font=("Arial", 14, "bold"),
            width=10, bg="lightgray"
        )
        self.like_button.pack(pady=20)
        ToolTip(self.like_button, "Shortcut: 1")

    def create_additional_buttons(self):
        """Create additional buttons for jumping to liked images and exporting."""
        additional_frame = tk.Frame(self.main_frame)
        additional_frame.pack(pady=10)

        jump_button = tk.Button(
            additional_frame, text="Jump to Last Liked", command=self.jump_to_last_liked, font=("Arial", 10)
        )
        jump_button.pack(side=tk.LEFT, padx=5)

        export_button = tk.Button(
            additional_frame, text="FINISH (Export Liked Images)", command=self.export_liked_images, font=("Arial", 10)
        )
        export_button.pack(side=tk.LEFT, padx=5)

        ToolTip(export_button, "Export to a folder inside the current folder")

    def show_current_image(self):
        """Display the current image and update the UI."""
        if not self.images:
            return

        image = Image.open(self.images[self.current_index])
        image = ImageOps.exif_transpose(image)
        display_size = (800, 600)
        image.thumbnail(display_size, Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo

        self.update_progress_bar()
        self.update_status()
        self.update_like_button()

    def update_progress_bar(self):
        """Update the progress bar to reflect the current image index."""
        self.progress["value"] = (self.current_index + 1) / len(self.images) * 100

    def update_status(self):
        """Update the status label with the current image information."""
        self.status_label.config(
            text=f"Image {self.current_index + 1} of {len(self.images)}"
        )

    def update_like_button(self):
        """Update the like button appearance based on the current image's like status."""
        if self.images[self.current_index] in self.liked_images:
            self.like_button.config(text="❤️ Liked", bg="lightgreen")
        else:
            self.like_button.config(text="🤍 Like", bg="lightgray")

    def move_image(self, delta):
        """Move to the next or previous image."""
        new_index = self.current_index + delta
        if 0 <= new_index < len(self.images):
            self.current_index = new_index
            self.progress_var.set(new_index)  # Update the progress bar value
            self.show_current_image()

    def toggle_like(self):
        """Toggle the like status of the current image."""
        current_image = self.images[self.current_index]
        if current_image in self.liked_images:
            self.liked_images.remove(current_image)
        else:
            self.liked_images.add(current_image)
        self.save_likes()
        self.show_current_image()

    def update_image_from_progress(self, event):
        """Update the current image based on the progress bar position."""
        progress_width = self.progress.winfo_width()
        click_x = event.x
        new_value = max(0, min(click_x / progress_width, 1)) * (len(self.images) - 1)
        new_index = int(new_value)

        if 0 <= new_index < len(self.images):
            self.current_index = new_index
            self.progress_var.set(new_index)
            self.show_current_image()

    def jump_to_last_liked(self):
        """Jump to the last liked image."""
        for i in range(len(self.images) - 1, -1, -1):
            if self.images[i] in self.liked_images:
                self.current_index = i
                self.progress_var.set(self.current_index)  # Update the progress bar value
                self.show_current_image()
                break

    def export_liked_images(self):
        """Export liked images to a folder."""
        if not self.liked_images:
            messagebox.showinfo("Info", "No liked images to export!")
            return

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