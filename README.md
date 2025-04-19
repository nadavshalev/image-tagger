# Image Tagger

## Overview
Image Tagger is a Python-based application that allows users to browse, tag, and organize images in a selected folder. Users can "like" images, navigate through them, and export their liked images to a separate folder for easy access.

The application is built using the `tkinter` library for the graphical user interface and the `Pillow` library for image processing.

---

## Features
- **Image Tagging**: Like or unlike images and save the liked images to a JSON file.
- **Keyboard Shortcuts**: Navigate and tag images quickly using keyboard shortcuts.
- **Image Navigation**: Move between images using buttons or keyboard shortcuts.
- **Export Liked Images**: Export all liked images to a separate folder.

---

## Installation

1. **Python 3.7 or higher** must be installed on your system.
2. clone the repo:
    ```bash
   git clone https://github.com/nadavshalev/image-tagger.git
   ```
3. Navigate to the project directory:
   ```bash
    cd image-tagger
    ```
4. Install the required libraries using pip:
   ```bash
   pip install -r requirements.txt
   ```
   
## Usage
### Run the application:
   ```bash
   python image_tagger.py
   ```
### Start new session:
1. Insert your name in the input field 
2. Select a folder containing images

### Tagg your images:
- Like or unlike images
  - click the "Like" button
  - press the `1` key on your keyboard
- Go to the next image
  - click the "Next" button
  - press the `Right Arrow` key on your keyboard
- Go to the previous image
  - click the "Previous" button
  - press the `Left Arrow` key on your keyboard
- Move between distant images
  - click on the progress bar

### Export liked images:
1. Click the "FINISH" button to save all liked images to a separate folder.