import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
import os
from PIL import Image, ImageTk
import Facal_recgnition

SETTINGS_FILE = "settings.json"
file_paths_store = []
cropped_images_cache = {}  # Store cropped images in memory
error_messages_cache = {}  # Store error messages for failed crops


# -------- Settings Load/Save --------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    else:
        return {"width": 500, "height": 500}  # Default values


def save_settings(width, height):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({"width": width, "height": height}, f)


# -------- Main App Window --------
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Face Recognition Batch Cropper")
        self.geometry("530x350")
        self.resizable(0, 0)

        # Load settings
        self.settings = load_settings()
        self.output_path = tk.StringVar()

        # Menu Bar
        self.create_menu()

        # Layout


        tk.Label(self, text="Output location").grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(self, textvariable=self.output_path, width=40).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self, text="Select Folder", command=self.browse_output_location).grid(row=0, column=2, padx=10)
        
        tk.Label(self, text="Input files").grid(row=1, column=0, padx=10, pady=5)
        tk.Button(self, text="Browse Input Files", command=self.browse_input_files).grid(row=1, column=1, padx=10)
        # Table
        self.table_frame = ttk.Frame(self)
        self.table_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        columns = ('Image Name', 'Status')
        self.table = ttk.Treeview(self.table_frame, columns=columns, show='headings')
        self.table.heading('Image Name', text='Image Name')
        self.table.heading('Status', text='Status')
        self.table.column('Image Name', width=400)
        self.table.column('Status', width=100)

        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind click event to table
        self.table.bind('<Double-Button-1>', self.handle_table_click)

        # Buttons
        tk.Button(self, text="Crop All", command=self.crop_all_images).grid(row=3, column=0, pady=10)
        tk.Button(self, text="Clear", command=self.clear_files).grid(row=3, column=2, pady=10)

    # -------- Menu Bar --------
    def create_menu(self):
        menubar = tk.Menu(self)

        menu = tk.Menu(menubar, tearoff=0)
        menu.add_command(label="Settings", command=self.open_settings)
        menu.add_command(label="About", command=self.open_about)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.quit)

        menubar.add_cascade(label="Menu", menu=menu)
        self.config(menu=menubar)

    # -------- File Browsing --------
    def browse_input_files(self):
        global file_paths_store
        files = filedialog.askopenfilenames(
            title="Select Input Files",
            filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*"))
        )
        if files:
            file_paths_store = list(files)
            for item in self.table.get_children():
                self.table.delete(item)
            for file in files:
                filename = os.path.basename(file)
                self.table.insert('', tk.END, values=(filename, 'File loaded'))

    def browse_output_location(self):
        folder = filedialog.askdirectory(title="Select Output Location")
        if folder:
            self.output_path.set(folder)

    # -------- Clear Functionality --------
    def clear_files(self):
        global file_paths_store, cropped_images_cache, error_messages_cache
        file_paths_store = []
        cropped_images_cache = {}
        error_messages_cache = {}
        for item in self.table.get_children():
            self.table.delete(item)

    # -------- Handle Table Click --------
    def handle_table_click(self, event):
        selected_item = self.table.selection()
        if not selected_item:
            return
        
        filename = self.table.item(selected_item[0])['values'][0]
        status = self.table.item(selected_item[0])['values'][1]
        
        # Show preview if image was successfully cropped
        if status == '✓':
            self.show_preview(filename)
        # Show error if cropping failed
        elif status == '✘':
            self.show_error(filename)
        else:
            messagebox.showinfo("Info", "Please crop the image first")

    # -------- Preview Functionality --------
    def show_preview(self, filename):
        # Find the original file path
        original_path = None
        for path in file_paths_store:
            if os.path.basename(path) == filename:
                original_path = path
                break
        
        if not original_path or filename not in cropped_images_cache:
            messagebox.showerror("Error", "Could not find image data")
            return
        
        # Open preview window
        PreviewDialog(self, original_path, cropped_images_cache[filename], filename)

    # -------- Error Display --------
    def show_error(self, filename):
        if filename in error_messages_cache:
            ErrorDialog(self, filename, error_messages_cache[filename])
        else:
            messagebox.showerror("Error", "No error information available for this image")

    # -------- Crop Functionality --------
    def crop_all_images(self):
        global cropped_images_cache, error_messages_cache
        output_directory = self.output_path.get()
        width, height = self.settings.get("width", 500), self.settings.get("height", 500)

        if not output_directory:
            messagebox.showerror("Error", "Please select an output directory first")
            return
        if not file_paths_store:
            messagebox.showerror("Error", "Please select input files first")
            return

        for file_path in file_paths_store:
            filename = os.path.basename(file_path)
            try:
                cropped_image = Facal_recgnition.crop_image(file_path, width, height)
                if cropped_image:
                    save_path = os.path.join(output_directory, filename)
                    cropped_image.save(save_path)
                    
                    # Cache the cropped image for preview
                    cropped_images_cache[filename] = cropped_image.copy()
                    
                    # Remove any previous error for this file
                    if filename in error_messages_cache:
                        del error_messages_cache[filename]
                    
                    for item in self.table.get_children():
                        if self.table.item(item)['values'][0] == filename:
                            self.table.item(item, values=(filename, '✓'))
                else:
                    # No face detected or other issue
                    error_messages_cache[filename] = "No face detected in the image"
                    for item in self.table.get_children():
                        if self.table.item(item)['values'][0] == filename:
                            self.table.item(item, values=(filename, '✘'))
            except Exception as e:
                # Store the error message
                error_messages_cache[filename] = str(e)
                for item in self.table.get_children():
                    if self.table.item(item)['values'][0] == filename:
                        self.table.item(item, values=(filename, '✘'))
                print(f"Error processing {file_path}: {str(e)}")

    # -------- Open Dialogs --------
    def open_settings(self):
        SettingsDialog(self, self.settings)

    def open_about(self):
        AboutDialog(self)


# -------- Error Dialog --------
class ErrorDialog(tk.Toplevel):
    def __init__(self, parent, filename, error_message):
        super().__init__(parent)
        self.title(f"Error - {filename}")
        self.geometry("500x250")
        self.resizable(0, 0)
        self.grab_set()

        # Header
        tk.Label(self, text="❌ Cropping Failed", font=("Arial", 14, "bold"), fg="red").pack(pady=20)

        # Filename
        tk.Label(self, text=f"File: {filename}", font=("Arial", 10)).pack(pady=5)

        # Error message frame
        error_frame = tk.Frame(self, bg="white", relief=tk.SUNKEN, borderwidth=2)
        error_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(error_frame, text="Error Details:", font=("Arial", 10, "bold"), bg="white", anchor='w').pack(padx=10, pady=5, fill=tk.X)
        
        # Scrollable text widget for error message
        error_text = tk.Text(error_frame, height=5, wrap=tk.WORD, bg="white", relief=tk.FLAT)
        error_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        error_text.insert(1.0, error_message)
        error_text.config(state=tk.DISABLED)

        # Close button
        tk.Button(self, text="Close", command=self.destroy, width=10).pack(pady=10)


# -------- Preview Dialog --------
class PreviewDialog(tk.Toplevel):
    def __init__(self, parent, original_path, cropped_image, filename):
        super().__init__(parent)
        self.title(f"Preview - {filename}")
        self.geometry("900x500")
        self.grab_set()

        # Main container
        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Before section
        before_frame = tk.Frame(container)
        before_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(before_frame, text="Before", font=("Arial", 12, "bold")).pack(pady=5)
        before_canvas = tk.Canvas(before_frame, width=400, height=400, bg='gray85')
        before_canvas.pack()

        # After section
        after_frame = tk.Frame(container)
        after_frame.pack(side=tk.RIGHT, padx=10, fill=tk.BOTH, expand=True)
        
        tk.Label(after_frame, text="After", font=("Arial", 12, "bold")).pack(pady=5)
        after_canvas = tk.Canvas(after_frame, width=400, height=400, bg='gray85')
        after_canvas.pack()

        # Load and display images
        try:
            # Original image
            original_img = Image.open(original_path)
            original_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            self.original_photo = ImageTk.PhotoImage(original_img)
            before_canvas.create_image(200, 200, image=self.original_photo)

            # Cropped image
            cropped_img = cropped_image.copy()
            cropped_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            self.cropped_photo = ImageTk.PhotoImage(cropped_img)
            after_canvas.create_image(200, 200, image=self.cropped_photo)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load images: {str(e)}")
            self.destroy()

        # Close button
        tk.Button(self, text="Close", command=self.destroy).pack(pady=10)


# -------- Settings Dialog --------
class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("300x200")
        self.settings = settings
        self.grab_set()

        tk.Label(self, text="⚙ Cropping Settings", font=("Arial", 13, "bold")).pack(pady=10)

        self.width_var = tk.IntVar(value=settings.get("width", 500))
        self.height_var = tk.IntVar(value=settings.get("height", 500))

        form = tk.Frame(self)
        form.pack(pady=10)

        tk.Label(form, text="Crop Width:").grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(form, textvariable=self.width_var).grid(row=0, column=1)

        tk.Label(form, text="Crop Height:").grid(row=1, column=0, padx=10, pady=5)
        tk.Entry(form, textvariable=self.height_var).grid(row=1, column=1)

        tk.Button(self, text="Save Settings", command=self.save_settings).pack(pady=10)

    def save_settings(self):
        width = self.width_var.get()
        height = self.height_var.get()
        if width <= 0 or height <= 0:
            messagebox.showerror("Error", "Width and height must be positive numbers")
            return
        save_settings(width, height)
        self.settings["width"] = width
        self.settings["height"] = height
        messagebox.showinfo("Saved", "Settings saved successfully!")
        self.destroy()


# -------- About Dialog --------
class AboutDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About")
        self.geometry("300x200")
        self.grab_set()

        tk.Label(self, text="ℹ About", font=("Arial", 14, "bold")).pack(pady=20)
        tk.Label(self, text="Face Recognition Batch Cropper\nVersion 1.0\nDeveloped by Arush Warty").pack(pady=10)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()