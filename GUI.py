import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
import os
import Facal_recgnition

SETTINGS_FILE = "settings.json"
file_paths_store = []


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
        self.geometry("600x480")
        self.resizable(0, 0)

        # Load settings
        self.settings = load_settings()
        self.output_path = tk.StringVar()

        # Menu Bar
        self.create_menu()

        # Layout
        tk.Label(self, text="Please put input files here").grid(row=0, column=0, padx=10, pady=5)
        tk.Button(self, text="Browse Input Files", command=self.browse_input_files).grid(row=0, column=1, padx=10)

        tk.Label(self, text="Output location").grid(row=1, column=0, padx=10, pady=5)
        tk.Entry(self, textvariable=self.output_path, width=40).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self, text="Select Folder", command=self.browse_output_location).grid(row=1, column=2, padx=10)

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

        # Buttons
        tk.Button(self, text="Crop All", command=self.crop_all_images).grid(row=3, column=1, pady=10)

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

    # -------- Crop Functionality --------
    def crop_all_images(self):
        output_directory = self.output_path.get()
        width, height = self.settings.get("width", 500), self.settings.get("height", 500)

        if not output_directory:
            messagebox.showerror("Error", "Please select an output directory first")
            return
        if not file_paths_store:
            messagebox.showerror("Error", "Please select input files first")
            return

        for file_path in file_paths_store:
            try:
                cropped_image = Facal_recgnition.crop_image(file_path, width, height)
                if cropped_image:
                    filename = os.path.basename(file_path)
                    save_path = os.path.join(output_directory, filename)
                    cropped_image.save(save_path)
                    for item in self.table.get_children():
                        if self.table.item(item)['values'][0] == filename:
                            self.table.item(item, values=(filename, '✓'))
            except Exception as e:
                filename = os.path.basename(file_path)
                for item in self.table.get_children():
                    if self.table.item(item)['values'][0] == filename:
                        self.table.item(item, values=(filename, '✘'))
                print(f"Error processing {file_path}: {str(e)}")

    # -------- Open Dialogs --------
    def open_settings(self):
        SettingsDialog(self, self.settings)

    def open_about(self):
        AboutDialog(self)


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
